/* ===================================================================
   Hệ thống chấm công định vị 3D — giao diện web
   Đồ án IE402, nhóm 1
   =================================================================== */

var API = "";                 // cùng origin với máy chủ
var token = localStorage.getItem("token") || null;
var toi = null;               // thông tin nhân viên đang đăng nhập
var khuVuc = [];              // danh sách khối MAP
var viTriMoPhong = null;      // toạ độ do người dùng bấm trên bản đồ
var dangChoBamBanDo = false;
var view = null, lopDiem = null, lopKhoi = null;

/* ---------------- gọi API ---------------- */
async function api(duong, tuyChon) {
  tuyChon = tuyChon || {};
  var headers = Object.assign({ "Content-Type": "application/json" }, tuyChon.headers || {});
  if (token) headers.Authorization = "Bearer " + token;
  var res = await fetch(API + duong, Object.assign({}, tuyChon, { headers: headers }));
  var data = null;
  try { data = await res.json(); } catch (e) { data = null; }
  if (!res.ok) {
    if (res.status === 401) dangXuat();
    throw new Error((data && data.loi) || "Lỗi " + res.status);
  }
  return data;
}

var $ = function (id) { return document.getElementById(id); };

/* ===================================================================
   1. ĐĂNG NHẬP
   =================================================================== */
document.querySelectorAll(".goi-y a").forEach(function (a) {
  a.addEventListener("click", function (e) {
    e.preventDefault();
    $("tenDangNhap").value = a.dataset.tk;
    $("matKhau").value = "123456";
  });
});

$("formDangNhap").addEventListener("submit", async function (e) {
  e.preventDefault();
  $("loiDangNhap").textContent = "";
  try {
    var kq = await api("/api/dang-nhap", {
      method: "POST",
      body: JSON.stringify({
        ten_dang_nhap: $("tenDangNhap").value.trim(),
        mat_khau: $("matKhau").value,
      }),
    });
    token = kq.token;
    localStorage.setItem("token", token);
    await vaoUngDung();
  } catch (err) {
    $("loiDangNhap").textContent = err.message;
  }
});

$("btnThoat").addEventListener("click", dangXuat);

function dangXuat() {
  token = null;
  localStorage.removeItem("token");
  $("ungDung").classList.add("an");
  $("manDangNhap").classList.remove("an");
}

/* ===================================================================
   2. VÀO ỨNG DỤNG
   =================================================================== */
async function vaoUngDung() {
  toi = await api("/api/toi");
  khuVuc = await api("/api/khu-vuc");

  $("manDangNhap").classList.add("an");
  $("ungDung").classList.remove("an");
  $("tenNguoiDung").textContent = toi.ho_ten;
  $("vaiTro").textContent = toi.vai_tro.replace("_", " ");

  // tab Quản lý chỉ dành cho quản lý / quản trị
  var laQuanLy = toi.vai_tro === "QUAN_LY" || toi.vai_tro === "QUAN_TRI";
  document.querySelectorAll(".chi-quan-ly").forEach(function (el) {
    el.style.display = laQuanLy ? "" : "none";
  });

  $("thongTinLamViec").innerHTML = [
    ["Công ty", toi.ten_cong_ty],
    ["Văn phòng", toi.ten_van_phong],
    ["Toà nhà", toi.ten_toa_nha],
    ["Dải tầng", "Tầng " + toi.tang_bat_dau + "–" + toi.tang_ket_thuc],
    ["Dải cao độ khối", Number(toi.z_min).toFixed(2) + " – " + Number(toi.z_max).toFixed(2) + " m"],
    ["Dung sai", "δxy " + Number(toi.dung_sai_ngang) + " m · δz " + Number(toi.dung_sai_dung) + " m"],
  ].map(function (r) {
    return "<div><dt>" + r[0] + "</dt><dd>" + r[1] + "</dd></div>";
  }).join("");

  var tang = $("tang");
  tang.max = toi.so_tang;
  tang.value = Math.min(Math.max(toi.tang_bat_dau, 1), toi.so_tang);
  capNhatTang();

  dungBanDo();
  await taiLichSu();
  if (laQuanLy) await taiQuanLy();
}

/* ===================================================================
   3. TAB
   =================================================================== */
document.querySelectorAll(".tab button").forEach(function (b) {
  b.addEventListener("click", function () {
    document.querySelectorAll(".tab button").forEach(function (x) { x.classList.remove("chon"); });
    b.classList.add("chon");
    ["chamcong", "lichsu", "quanly"].forEach(function (t) {
      $("tab-" + t).classList.toggle("an", t !== b.dataset.tab);
    });
    if (b.dataset.tab === "lichsu") taiLichSu();
    if (b.dataset.tab === "quanly") taiQuanLy();
  });
});

/* ===================================================================
   4. CHẤM CÔNG
   =================================================================== */
function caoDoCuaTang(t) {
  return Number(toi.cao_do_nen) + (t - 0.5) * Number(toi.chieu_cao_tang);
}
function capNhatTang() {
  var t = Number($("tang").value);
  $("tangHienThi").textContent = t;
  $("caoDoSuyRa").textContent =
    "Cao độ suy ra từ tầng: " + caoDoCuaTang(t).toFixed(2) + " m " +
    "(dùng khi thiết bị không đo được cao độ)";
}
$("tang").addEventListener("input", capNhatTang);

var nguonViTri = "GPS";
$("btnGps").addEventListener("click", function () {
  nguonViTri = "GPS";
  dangChoBamBanDo = false;
  $("btnGps").classList.add("chon");
  $("btnMoPhong").classList.remove("chon");
  $("btnMoPhong").textContent = "Mô phỏng (bấm bản đồ)";
});
$("btnMoPhong").addEventListener("click", function () {
  nguonViTri = "MO_PHONG";
  dangChoBamBanDo = true;
  $("btnMoPhong").classList.add("chon");
  $("btnGps").classList.remove("chon");
  $("btnMoPhong").textContent = "Đang chờ… bấm lên bản đồ";
});

$("btnVao").addEventListener("click", function () { chamCong("VAO"); });
$("btnRa").addEventListener("click", function () { chamCong("RA"); });

// Định danh thiết bị: ổn định trên cùng trình duyệt, đủ để minh hoạ quy tắc R4.
function dinhDanhThietBi() {
  var d = localStorage.getItem("thiet_bi");
  if (!d) {
    d = "web-" + Math.random().toString(36).slice(2, 10);
    localStorage.setItem("thiet_bi", d);
  }
  return d;
}

async function layViTri() {
  if (nguonViTri === "MO_PHONG") {
    if (!viTriMoPhong) throw new Error("Chưa chọn vị trí mô phỏng — bấm lên bản đồ trước");
    return {
      kinh_do: viTriMoPhong.kinh_do,
      vi_do: viTriMoPhong.vi_do,
      cao_do: caoDoCuaTang(Number($("tang").value)),
      do_chinh_xac_ngang: 8,
      do_chinh_xac_dung: null,
      nguon_cao_do: "KHAI_BAO",
    };
  }
  var pos = await new Promise(function (ok, er) {
    if (!navigator.geolocation) return er(new Error("Trình duyệt không hỗ trợ định vị"));
    navigator.geolocation.getCurrentPosition(ok, function (e) {
      er(new Error("Không lấy được vị trí: " + e.message +
        " (Geolocation chỉ chạy trên HTTPS hoặc localhost)"));
    }, { enableHighAccuracy: true, timeout: 10000 });
  });
  var c = pos.coords;
  // Cao độ GPS trong nhà thường không dùng được -> rơi về tầng khai báo.
  var dungDuoc = c.altitude !== null && c.altitudeAccuracy !== null && c.altitudeAccuracy < 15;
  return {
    kinh_do: c.longitude,
    vi_do: c.latitude,
    cao_do: dungDuoc ? c.altitude : caoDoCuaTang(Number($("tang").value)),
    do_chinh_xac_ngang: c.accuracy,
    do_chinh_xac_dung: c.altitudeAccuracy,
    nguon_cao_do: dungDuoc ? "THIET_BI" : "KHAI_BAO",
  };
}

async function chamCong(loai) {
  var o = $("ketQua");
  o.className = "ket-qua";
  o.innerHTML = "Đang xác thực vị trí…";
  try {
    var vt = await layViTri();
    var kq = await api("/api/cham-cong", {
      method: "POST",
      body: JSON.stringify(Object.assign({}, vt, {
        loai: loai,
        tang_khai_bao: Number($("tang").value),
        dinh_danh_thiet_bi: dinhDanhThietBi(),
      })),
    });
    hienKetQua(kq, loai);
    veDiem(vt.kinh_do, vt.vi_do, kq.cao_do, kq.trang_thai);
    taiLichSu();
  } catch (err) {
    o.className = "ket-qua kq-xau";
    o.innerHTML = "<b>Không chấm công được</b>" + err.message;
  }
}

function hienKetQua(kq, loai) {
  var lop = { HOP_LE: "kq-ok", NGHI_NGO: "kq-ngo", NGOAI_VUNG: "kq-xau" }[kq.trang_thai];
  var tieuDe = {
    HOP_LE: "HỢP LỆ — đã ghi nhận chấm công " + loai,
    NGHI_NGO: "NGHI NGỜ — đúng toà nhà, sai tầng",
    NGOAI_VUNG: "NGOÀI VÙNG — từ chối",
  }[kq.trang_thai];

  var ct = "Khoảng cách ngang tới khối: <b>" + kq.khoang_cach_ngang + " m</b> " +
    "(δxy = " + kq.dung_sai.ngang + " m)<br/>" +
    "Cao độ: <b>" + kq.cao_do + " m</b> · dải khối " +
    kq.dai_khoi.z_min.toFixed(2) + "–" + kq.dai_khoi.z_max.toFixed(2) + " m " +
    "(δz = " + kq.dung_sai.dung + " m)";
  if (kq.lech_cao_do) {
    ct += "<br/>Lệch cao độ: <b>" + (kq.lech_cao_do > 0 ? "+" : "") + kq.lech_cao_do + " m</b>";
  }
  if (kq.canh_bao.length) {
    ct += "<ul class='cb-list'>" + kq.canh_bao.map(function (c) {
      return "<li><b>" + c.ma_quy_tac + "</b> (" + c.muc_do + "): " + c.mo_ta + "</li>";
    }).join("") + "</ul>";
  }
  ct += "<small>Nguồn cao độ: " +
    (kq.nguon_cao_do === "THIET_BI" ? "thiết bị đo được" : "tầng khai báo") +
    " · mã bản ghi #" + kq.ma_ban_ghi + "</small>";

  var o = $("ketQua");
  o.className = "ket-qua " + lop;
  o.innerHTML = "<b>" + tieuDe + "</b>" + ct;
}

/* ===================================================================
   5. BẢN ĐỒ 3D
   =================================================================== */
function dungBanDo() {
  if (view) return;
  require([
    "esri/Map", "esri/views/SceneView", "esri/layers/GraphicsLayer",
    "esri/Graphic", "esri/geometry/Polygon", "esri/geometry/Point",
  ], function (Map, SceneView, GraphicsLayer, Graphic, Polygon, Point) {

    lopKhoi = new GraphicsLayer({ elevationInfo: { mode: "absolute-height" } });
    lopDiem = new GraphicsLayer({ elevationInfo: { mode: "absolute-height" } });

    var map = new Map({
      basemap: "topo-vector",
      ground: "world-elevation",
      layers: [lopKhoi, lopDiem],
    });

    var mau = [[232, 98, 42], [31, 111, 235], [130, 80, 223], [26, 127, 55]];
    var tam = null;

    khuVuc.forEach(function (k, i) {
      var hinh = JSON.parse(k.da_giac_nen);
      var zMin = Number(k.z_min), zMax = Number(k.z_max);
      var rings = hinh.coordinates.map(function (r) {
        return r.map(function (p) { return [p[0], p[1], zMin]; });
      });
      if (!tam) tam = rings[0][0];

      var laCuaToi = k.ma_khu_vuc === toi.ma_khu_vuc;
      var c = mau[i % mau.length];

      lopKhoi.add(new Graphic({
        geometry: new Polygon({ rings: rings, spatialReference: { wkid: 4326 } }),
        symbol: {
          type: "polygon-3d",
          symbolLayers: [{
            type: "extrude",
            size: zMax - zMin,
            material: { color: c.concat([laCuaToi ? 0.6 : 0.3]) },
            edges: { type: "solid", size: laCuaToi ? 1.6 : 0.8, color: c.concat([1]) },
          }],
        },
        popupTemplate: {
          title: k.ten_van_phong,
          content:
            "<b>Công ty:</b> " + k.ten_cong_ty + "<br/>" +
            "<b>Toà nhà:</b> " + k.ten_toa_nha + "<br/>" +
            "<b>Dải tầng:</b> " + k.tang_bat_dau + "–" + k.tang_ket_thuc + "<br/>" +
            "<b>z_min:</b> " + zMin.toFixed(2) + " m<br/>" +
            "<b>z_max:</b> " + zMax.toFixed(2) + " m<br/>" +
            "<b>Dung sai:</b> δxy " + k.dung_sai_ngang + " m · δz " + k.dung_sai_dung + " m",
        },
      }));
    });

    view = new SceneView({
      container: "banDo",
      map: map,
      camera: {
        position: [tam[0] - 0.0016, tam[1] - 0.0016, 320],
        heading: 40, tilt: 68,
      },
    });
    view.ui.move("zoom", "top-right");

    view.on("click", function (e) {
      if (!dangChoBamBanDo || !e.mapPoint) return;
      viTriMoPhong = { kinh_do: e.mapPoint.longitude, vi_do: e.mapPoint.latitude };
      dangChoBamBanDo = false;
      $("btnMoPhong").textContent = "Mô phỏng: đã chọn vị trí";
      veDiem(viTriMoPhong.kinh_do, viTriMoPhong.vi_do,
             caoDoCuaTang(Number($("tang").value)), "CHUA_CHAM");
    });

    window.ungDung = { view: view, api: api, chamCong: chamCong };
  });
}

function veDiem(lon, lat, z, trangThai) {
  if (!lopDiem) return;
  require(["esri/Graphic", "esri/geometry/Point"], function (Graphic, Point) {
    var c = { HOP_LE: [26, 127, 55], NGHI_NGO: [212, 167, 44],
              NGOAI_VUNG: [207, 34, 46] }[trangThai] || [90, 100, 110];
    lopDiem.add(new Graphic({
      geometry: new Point({ longitude: lon, latitude: lat, z: z,
                            spatialReference: { wkid: 4326 } }),
      symbol: {
        type: "point-3d",
        symbolLayers: [{
          type: "object", resource: { primitive: "sphere" },
          material: { color: c }, width: 5, depth: 5, height: 5,
        }],
      },
    }));
  });
}

/* ===================================================================
   6. LỊCH SỬ
   =================================================================== */
async function taiLichSu() {
  var rows = await api("/api/cham-cong/lich-su");
  var tb = $("bangLichSu").querySelector("tbody");
  if (!rows.length) {
    tb.innerHTML = "<tr><td colspan='7' style='color:#8c959f'>Chưa có bản ghi nào</td></tr>";
    return;
  }
  tb.innerHTML = rows.map(function (r) {
    var nhan = { HOP_LE: "n-ok", NGHI_NGO: "n-ngo", NGOAI_VUNG: "n-xau" }[r.trang_thai];
    var nutDon = "";
    if (r.trang_thai !== "HOP_LE" && !r.trang_thai_don) {
      nutDon = "<button class='btn nho' onclick='guiGiaiTrinh(" + r.ma_ban_ghi + ")'>Gửi giải trình</button>";
    } else if (r.trang_thai_don) {
      nutDon = r.trang_thai_don.replace("_", " ");
    }
    return "<tr>" +
      "<td>" + new Date(r.thoi_diem).toLocaleString("vi-VN") + "</td>" +
      "<td>" + r.loai + "</td>" +
      "<td>" + (r.tang_khai_bao || "—") + "</td>" +
      "<td>" + (r.cao_do === null ? "—" : Number(r.cao_do).toFixed(2) + " m") + "</td>" +
      "<td><span class='nhan " + nhan + "'>" + r.trang_thai + "</span></td>" +
      "<td>" + (r.so_canh_bao > 0 ? r.so_canh_bao : "—") + "</td>" +
      "<td>" + nutDon + "</td></tr>";
  }).join("");
}

window.guiGiaiTrinh = async function (maBanGhi) {
  var lyDo = prompt("Lý do giải trình cho bản ghi #" + maBanGhi + ":");
  if (!lyDo) return;
  try {
    await api("/api/giai-trinh", {
      method: "POST",
      body: JSON.stringify({ ma_ban_ghi: maBanGhi, ly_do: lyDo }),
    });
    alert("Đã gửi đơn giải trình, chờ quản lý duyệt.");
    taiLichSu();
  } catch (e) { alert(e.message); }
};

/* ===================================================================
   7. QUẢN LÝ
   =================================================================== */
async function taiQuanLy() {
  if (toi.vai_tro !== "QUAN_LY" && toi.vai_tro !== "QUAN_TRI") return;

  var db = await api("/api/dashboard");
  var dem = {};
  db.theo_trang_thai.forEach(function (r) { dem[r.trang_thai] = r.so_luong; });
  var soCanhBao = db.theo_quy_tac.reduce(function (a, r) { return a + r.so_luong; }, 0);
  var choDuyet = (db.don_giai_trinh.find(function (r) { return r.trang_thai === "CHO_DUYET"; }) || {}).so_luong || 0;

  $("oSo").innerHTML = [
    ["Hợp lệ", dem.HOP_LE || 0], ["Nghi ngờ", dem.NGHI_NGO || 0],
    ["Ngoài vùng", dem.NGOAI_VUNG || 0], ["Cảnh báo", soCanhBao],
    ["Đơn chờ duyệt", choDuyet],
  ].map(function (o) {
    return "<div class='o'><b>" + o[1] + "</b><span>" + o[0] + "</span></div>";
  }).join("");

  var cb = await api("/api/canh-bao");
  $("bangCanhBao").querySelector("tbody").innerHTML = cb.length ? cb.map(function (r) {
    return "<tr>" +
      "<td><span class='nhan " + (r.muc_do === "CAO" ? "n-cao" : "n-tb") + "'>" + r.muc_do + "</span></td>" +
      "<td><b>" + r.ma_quy_tac + "</b></td>" +
      "<td>" + r.ho_ten + "</td>" +
      "<td>" + new Date(r.thoi_diem).toLocaleString("vi-VN") + "</td>" +
      "<td>" + r.mo_ta + "</td>" +
      "<td>" + (r.da_xu_ly ? "rồi" : "chưa") + "</td></tr>";
  }).join("") : "<tr><td colspan='6' style='color:#8c959f'>Chưa có cảnh báo</td></tr>";

  var don = await api("/api/giai-trinh?trang_thai=CHO_DUYET");
  $("bangDon").querySelector("tbody").innerHTML = don.length ? don.map(function (r) {
    return "<tr>" +
      "<td>" + r.ho_ten + "</td>" +
      "<td>#" + r.ma_ban_ghi + " · " + r.trang_thai_ban_ghi + "</td>" +
      "<td>" + r.ly_do + "</td>" +
      "<td>" + r.trang_thai + "</td>" +
      "<td><button class='btn nho' onclick='duyet(" + r.ma_don + ",\"DA_DUYET\")'>Duyệt</button> " +
      "<button class='btn nho' onclick='duyet(" + r.ma_don + ",\"TU_CHOI\")'>Từ chối</button></td>" +
      "</tr>";
  }).join("") : "<tr><td colspan='5' style='color:#8c959f'>Không có đơn chờ duyệt</td></tr>";

  var bc = await api("/api/bao-cao/cong");
  $("bangBaoCao").querySelector("tbody").innerHTML = bc.dong.map(function (r) {
    return "<tr><td>" + r.ho_ten + "</td><td>" + r.ten_cong_ty + "</td>" +
      "<td>" + r.so_lan_vao + "</td><td>" + r.hop_le + "</td>" +
      "<td>" + r.nghi_ngo + "</td><td>" + r.ngoai_vung + "</td>" +
      "<td>" + r.so_ngay_cong + "</td></tr>";
  }).join("");
}

window.duyet = async function (maDon, trangThai) {
  try {
    await api("/api/giai-trinh/" + maDon, {
      method: "PUT",
      body: JSON.stringify({ trang_thai: trangThai }),
    });
    taiQuanLy();
  } catch (e) { alert(e.message); }
};

/* ---------------- tự đăng nhập lại nếu còn phiên ---------------- */
if (token) {
  vaoUngDung().catch(function () { dangXuat(); });
}
