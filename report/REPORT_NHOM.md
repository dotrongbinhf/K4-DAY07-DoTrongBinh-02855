# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** [ví dụ: Customer support FAQ, Luật Việt Nam, công thức nấu ăn, ...]

**Tại sao nhóm chọn chủ đề này?**
> *Viết 2-3 câu:*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| 3 tài liệu chính sách Tiki đầu tiên (đã bỏ frontmatter) | FixedSizeChunker (`fixed_size`) | 7 | 485,14 ký tự | Có overlap nên ít mất thông tin ở ranh giới, nhưng có thể cắt giữa câu/mục. |
| 3 tài liệu chính sách Tiki đầu tiên (đã bỏ frontmatter) | SentenceChunker (`by_sentences`) | 11 | 279,91 ký tự | Giữ trọn câu, nhưng không bảo đảm giữ chung một section chính sách. |
| 3 tài liệu chính sách Tiki đầu tiên (đã bỏ frontmatter) | RecursiveChunker (`recursive`) | 11 | 279,91 ký tự | Ưu tiên ranh giới đoạn/câu nên chunk mạch lạc hơn khi văn bản có cấu trúc. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Đỗ Trọng Bình]**
- **Loại chiến lược:** Custom `HeadingChunker` (heading/section + RecursiveChunker fallback)
- **Mô tả & lý do chọn cho chủ đề này:** Tôi chọn HeadingChunker vì tài liệu chính sách Tiki có các mục rõ ràng, ví dụ Điều kiện, Thời hạn xử lý và Khiếu nại/bồi thường; heading giúp biết chunk đang nói về nội dung nào. Kết quả của tôi có 39 chunks và đạt 4/10: Q1, Q2, Q5 có context liên quan, còn Q3 và Q4 thất bại. Failure case rõ nhất là Q4: chunk top-1 chỉ có heading FBT, không có mốc 32 ngày, nên agent lấy nhầm thời hạn trong tài liệu Dropship.
- **Code snippet (nếu custom):**
```python
sections = re.split(r"(?m)(?=^#{1,6}\s+.+$)", text.strip())
if len(complete_section) > self.chunk_size:
    body_chunks = RecursiveChunker(chunk_size=available_size).chunk(body)
    chunks.extend(f"{heading}\n{body_chunk}" for body_chunk in body_chunks)
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|


**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Chương trình đổi trả 365 ngày áp dụng cho ngành hàng và nhà bán nào? | Áp dụng cho ngành Điện gia dụng và Thiết bị số thuộc nhà bán Tiki Trading. | `tiki-doi-tra-365` — `## Phạm vi và thời điểm áp dụng` |
| 2 | Khi từ chối yêu cầu đổi trả hoặc bảo hành, nhà bán Dropship cần cung cấp những loại bằng chứng hợp lệ nào? | Biên bản bàn giao/đồng kiểm; ảnh hoặc video đóng gói/khui mở; hoặc biên bản thẩm định của hãng. | `tiki-dropship-doi-tra-bao-hanh` — `## Điều kiện và trách nhiệm` |
| 3 | Nhà bán mô hình NGON cần làm gì khi hàng hoàn bị hư hỏng do lỗi vận chuyển? | Liên hệ Tiki trong 24 giờ, xác nhận thông tin/giá trị bồi thường và cung cấp hồ sơ, chứng từ qua Seller Center. | `tiki-ngon-doi-tra-boi-thuong` — `## Khiếu nại và bồi thường hàng hoàn` |
| 4 | Nhà bán FBT phải sắp xếp rút hàng trong thời hạn bao lâu? | Trong 32 ngày làm việc kể từ khi phiếu trả hàng được tạo. | `tiki-fbt-doi-tra-bao-hanh` — `## Hàng đổi trả` |
| 5 | Thời hạn đổi trả miễn phí là bao lâu? *(chạy A/B với `metadata_filter={"audience": "buyer"}`)* | 30 ngày đổi trả miễn phí; nguồn cũng nêu cam kết hoàn 200% nếu hàng giả. | `tiki-doi-tra-30-ngay` — toàn bộ tài liệu |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Phạm vi chương trình đổi trả 365 ngày | FixedSize | Có, top-1 | Chunk chứa đồng thời Điện gia dụng, Thiết bị số và Tiki Trading; agent trả lời đúng; 2/2. |
| 2 | Liệt kê bằng chứng Dropship | FixedSize | Có, top-2 | Chunk top-2 chứa đầy đủ ba loại bằng chứng; agent trả lời đúng; 1/2. |
| 3 | Xử lý hàng hoàn NGON hư hỏng khi vận chuyển | Không có | Không | Top-3 không có hành động 24 giờ/bồi thường; agent trả lời sai; 0/2. |
| 4 | Thời hạn rút hàng FBT | FixedSize | Có, top-1 | Chunk có mốc 32 ngày làm việc; agent trả lời đúng; 2/2. |
| 5 | Thời hạn đổi trả miễn phí | FixedSize | Có, top-1 | Chunk có mốc 30 ngày; agent trả lời đúng và có trích dẫn; 2/2. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, ở câu 5 filter `audience=buyer` giữ nguyên chunk 30 ngày ở top-1 nhưng loại các chunk dành cho seller khỏi top-2/top-3 ở cả FixedSize, Recursive và Heading. Vì vậy filter tăng precision của ngữ cảnh, dù trong lần chạy này không thay đổi thứ hạng top-1 hay điểm context. Đây cũng cho thấy query hiện chưa phụ thuộc hoàn toàn vào filter; để kiểm chứng mạnh hơn, corpus cần một cặp tài liệu buyer/seller có cùng cách diễn đạt nhưng câu trả lời trái ngược hơn.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

**Bài học rút ra khi so sánh trong nhóm:**

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
