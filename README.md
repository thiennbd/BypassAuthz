# BypassAuthz - Burp Suite Extension

**BypassAuthz** là một extension cho Burp Suite giúp tự động hóa quá trình kiểm thử để tìm cách vượt qua các trang/API trả về mã lỗi HTTP `403 Forbidden` (hoặc các cơ chế chặn truy cập dựa trên authorization tương tự). Extension được xây dựng bằng Python (Jython) với giao diện trực quan tích hợp ngay trong Burp Suite.

## Kỹ thuật hỗ trợ

* **Path Manipulation**: Thử nghiệm chèn các ký tự đặc biệt vào đường dẫn hoặc truy vấn (ví dụ: `..;`, `%2e`, `%2f`, `;%09`, `*`, `.abcxyz`, v.v.) tại nhiều vị trí khác nhau trong path (trước/sau/giữa các dấu `/` và ở cuối path).
* **Header Manipulation**: Chèn hoặc thay thế các HTTP Headers giả lập IP hoặc cấu hình định tuyến (ví dụ: `X-Forwarded-For`, `X-Real-Ip`, `X-Client-IP`, `X-Forwarded-Proto`, v.v.).
* **HTTP Method Manipulation**: Thay đổi phương thức yêu cầu từ `GET` sang `POST` đi kèm `Content-Length: 0`.
* **Downgrade Protocol**: Hạ cấp giao thức kết nối xuống `HTTP/1.0` đồng thời xóa bỏ toàn bộ headers bổ sung.
* **Case Sensitive**: Thay đổi kiểu viết hoa/thường của đường dẫn (ví dụ: viết hoa chữ cái đầu `/Example/Demo` hoặc xen kẽ `/ExAmPlE/DeMo`).
* **Referer & Origin Spoofing**: Tự động sửa hoặc thêm các header `Referer` và `Origin` trỏ ngược lại chính URL của request hiện tại để đánh lừa bộ lọc của server.

Toàn bộ payload (Query Payloads / Header Payloads) đều có thể tùy chỉnh trực tiếp trên giao diện: thêm, xóa hoặc xóa toàn bộ danh sách trước khi chạy test.

## Giao diện kết quả

* **Bảng kết quả** hiển thị từng request đã gửi: method, path, loại payload, status code và content length. Các dòng có status code `200` được tô màu xanh để dễ nhận diện bypass thành công.
* Chọn một dòng trong bảng để xem chi tiết **Request/Response** tương ứng ở khung bên dưới.
* **Show Highlight Row**: nút toggle để lọc, chỉ hiển thị các dòng có status code `200` (bypass thành công).
* **Stop**: dừng ngay quá trình test đang chạy, không gửi thêm request nào sau khi bấm.
* **Clear Table**: xóa toàn bộ kết quả hiện có trong bảng.

## Hướng dẫn cài đặt

1. Đảm bảo bạn đã cấu hình môi trường **Jython** trong Burp Suite (Tab **Extensions** -> **Core extension settings** -> **Python environment**).
2. Vào tab **Extensions** -> **Installed** -> click **Add**.
3. Chọn **Extension type** là `Python` và tìm tới đường dẫn file `BypassAuthz.py`.
4. Nhấp **Next** để nạp extension.

## Hướng dẫn sử dụng

1. Tại tab **HTTP History** (hoặc bất kỳ tab nào có request), click chuột phải vào request bị chặn `403 Forbidden` -> Chọn **BypassAuthz**.
2. Di chuyển sang tab **BypassAuthz** trên menu chính của Burp Suite để theo dõi tiến trình kiểm thử và phân tích kết quả.
3. Có thể bấm **Stop** bất cứ lúc nào để ngưng quá trình test, hoặc bật **Show Highlight Row** để chỉ xem các request bypass thành công.

---

# BypassAuthz - Burp Suite Extension (English)

**BypassAuthz** is a Burp Suite extension designed to automate the process of bypassing `403 Forbidden` restrictions (or similar authorization-based access controls) on web pages or APIs. It is built in Python (Jython) and provides an intuitive GUI integrated directly into Burp Suite.

## Supported Techniques

* **Path Manipulation**: Try inserting special characters into the path or query string (e.g. `..;`, `%2e`, `%2f`, `;%09`, `*`, `.abcxyz`, etc.) at multiple positions in the path (before/after/between slashes and at the end).
* **Header Manipulation**: Inject or replace HTTP headers to spoof IP addresses or routing configurations (e.g. `X-Forwarded-For`, `X-Real-Ip`, `X-Client-IP`, `X-Forwarded-Proto`, etc.).
* **HTTP Method Manipulation**: Change the request method from `GET` to `POST` with `Content-Length: 0`.
* **Downgrade Protocol**: Downgrade the connection protocol to `HTTP/1.0` and remove all other HTTP headers.
* **Case Sensitive**: Alternate casing of the path segments (e.g., capitalize first letters `/Example/Demo` or alternate case `/ExAmPlE/DeMo`).
* **Referer & Origin Spoofing**: Modify or add `Referer` and `Origin` headers to point to the current request URL to bypass server filters.

All payloads (Query Payloads / Header Payloads) are fully customizable in the UI: add, remove, or clear the lists before running a scan.

## Results UI

* The **results table** lists every request sent: method, path, payload type, status code and content length. Rows with a `200` status code are highlighted in green for quick identification of a successful bypass.
* Select a row to inspect the matching **Request/Response** in the panel below.
* **Show Highlight Row**: a toggle button that filters the table to show only `200` status code rows (successful bypasses).
* **Stop**: immediately halts the running scan; no further requests are sent after it's clicked.
* **Clear Table**: clears all current results from the table.

## Installation Guide

1. Ensure you have configured the **Jython** environment in Burp Suite (Tab **Extensions** -> **Core extension settings** -> **Python environment**).
2. Navigate to **Extensions** -> **Installed** -> click **Add**.
3. Choose **Extension type** as `Python` and select the `BypassAuthz.py` file.
4. Click **Next** to load the extension.

## Usage Guide

1. In the **HTTP History** tab (or any other request tab), right-click on the request that returned a `403 Forbidden` status -> Select **BypassAuthz**.
2. Go to the **BypassAuthz** tab on the main Burp Suite menu to monitor the testing progress and analyze request/response details.
3. Click **Stop** at any time to halt the scan, or enable **Show Highlight Row** to view only the successfully bypassed requests.

---

# References
- https://blogs.jsmon.sh/403-bypass-tricks-every-bug-hunter-should-know/
- https://github.com/portswigger/403-bypasser
