# Bypass403 - Burp Suite Extension

**Bypass403** là một extension cho Burp Suite giúp tự động hóa quá trình kiểm thử để tìm cách vượt qua các trang/API trả về mã lỗi HTTP `403 Forbidden`. Extension được xây dựng bằng Python (Jython) với giao diện trực quan tích hợp ngay trong Burp Suite.

## Kỹ thuật hỗ trợ

*   **Path Manipulation**: Thử nghiệm chèn các ký tự đặc biệt vào đường dẫn hoặc truy vấn (ví dụ: `..;`, `%2e`, `%2f`, `;%09`, v.v.).
*   **Header Manipulation**: Chèn hoặc thay thế các HTTP Headers giả lập IP hoặc cấu hình định tuyến (ví dụ: `X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Proto`, v.v.).
*   **HTTP Method Manipulation**: Thay đổi phương thức yêu cầu từ `GET` sang `POST` đi kèm `Content-Length: 0`.
*   **Downgrade Protocol**: Hạ cấp giao thức kết nối xuống `HTTP/1.0` đồng thời xóa bỏ toàn bộ headers bổ sung.
*   **Case Sensitive**: Thay đổi kiểu viết hoa/thường của đường dẫn (ví dụ: viết hoa chữ cái đầu `/Example/Demo` hoặc xen kẽ `/ExAmPlE/DeMo`).
*   **Referer & Origin Spoofing**: Tự động sửa hoặc thêm các header `Referer` và `Origin` trỏ ngược lại chính URL của request hiện tại để đánh lừa bộ lọc của server.

## Hướng dẫn cài đặt

1.  Đảm bảo bạn đã cấu hình môi trường **Jython** trong Burp Suite (Tab **Extensions** -> **Core extension settings** -> **Python environment**).
2.  Vào tab **Extensions** -> **Installed** -> click **Add**.
3.  Chọn **Extension type** là `Python` và tìm tới đường dẫn file `Bypass403.py`.
4.  Nhấp **Next** để nạp extension.

## Hướng dẫn sử dụng

1.  Tại tab **HTTP History** (hoặc bất kỳ tab nào có request), click chuột phải vào request bị chặn `403 Forbidden` -> Chọn **Bypass 403**.
2.  Di chuyển sang tab **Bypass403** trên menu chính của Burp Suite để theo dõi tiến trình kiểm thử và phân tích kết quả.

---

# Bypass403 - Burp Suite Extension (English)

**Bypass403** is a Burp Suite extension designed to automate the process of bypassing `403 Forbidden` restrictions on web pages or APIs. It is built in Python (Jython) and provides an intuitive GUI integrated directly into Burp Suite.

## Supported Techniques

*   **Path Manipulation**: Try inserting special characters into the path or query string (e.g. `..;`, `%2e`, `%2f`, `;%09`, etc.).
*   **Header Manipulation**: Inject or replace HTTP headers to spoof IP addresses or routing configurations (e.g. `X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Proto`, etc.).
*   **HTTP Method Manipulation**: Change the request method from `GET` to `POST` with `Content-Length: 0`.
*   **Downgrade Protocol**: Downgrade the connection protocol to `HTTP/1.0` and remove all other HTTP headers.
*   **Case Sensitive**: Alternate casing of the path segments (e.g., capitalize first letters `/Example/Demo` or alternate case `/ExAmPlE/DeMo`).
*   **Referer & Origin Spoofing**: Modify or add `Referer` and `Origin` headers to point to the current request URL to bypass server filters.

## Installation Guide

1.  Ensure you have configured the **Jython** environment in Burp Suite (Tab **Extensions** -> **Core extension settings** -> **Python environment**).
2.  Navigate to **Extensions** -> **Installed** -> click **Add**.
3.  Choose **Extension type** as `Python` and select the `Bypass403.py` file.
4.  Click **Next** to load the extension.

## Usage Guide

1.  In the **HTTP History** tab (or any other request tab), right-click on the request that returned a `403 Forbidden` status -> Select **Bypass 403**.
2.  Go to the **Bypass403** tab on the main Burp Suite menu to monitor the testing progress and analyze request/response details.

---

# References
- https://blogs.jsmon.sh/403-bypass-tricks-every-bug-hunter-should-know/
- https://github.com/portswigger/403-bypasser