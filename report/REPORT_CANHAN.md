# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Cosine similarity cao nghĩa là hai vector embedding gần cùng hướng (góc giữa chúng nhỏ), chúng có ý nghĩa gần nhau, tương tự với nhau cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi muốn hoàn tiền cho đơn hàng này.
- Câu B: Tôi cần được trả lại tiền cho sản phẩm đã mua.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng cùng yêu cầu hoàn tiền cho một giao dịch mua hàng.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Chính sách đổi trả cho phép khách hàng gửi yêu cầu hoàn tiền.
- Câu B: Đội bóng thắng trận chung kết với tỉ số 2–0.
- Tại sao khác: Hai câu đề cập đến hai chủ đề không liên quan: chính sách thương mại điện tử và kết quả thể thao.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine đo mức độ cùng hướng của các embedding nên ít bị ảnh hưởng bởi độ lớn vector, vốn có thể thay đổi theo độ dài văn bản hoặc đặc tính của mô hình. Vì truy xuất văn bản thường cần so sánh hướng ngữ nghĩa, cosine thường phù hợp hơn Euclid.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Bước dịch giữa hai chunk là `500 - 50 = 450` ký tự. Số chunk là `ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11...)`.
> *Đáp án:* **23 chunks**. Kết quả này cũng khớp với `FixedSizeChunker(chunk_size=500, overlap=50)` trong repo.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Khi overlap là 100, bước dịch còn `500 - 100 = 400`, nên có `ceil((10.000 - 100) / 400) = ceil(24,75) = 25` chunks — tăng từ 23 lên 25. Overlap lớn hơn giúp thông tin ở ranh giới giữa hai chunk xuất hiện ở cả hai phía, giảm nguy cơ tách rời ngữ cảnh hoặc câu trả lời; đổi lại sẽ tạo nhiều vector hơn và tăng chi phí lưu trữ/tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách câu sau dấu `.`, `!` hoặc `?` khi phía sau là khoảng trắng; dấu câu vẫn được giữ lại trong nội dung. Sau đó tôi gom tối đa `max_sentences_per_chunk` câu thành một chunk và loại bỏ khoảng trắng thừa. Nếu văn bản rỗng hoặc chỉ có khoảng trắng thì hàm trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi ưu tiên tách theo đoạn văn (`\n\n`), xuống dòng, câu, khoảng trắng rồi cuối cùng mới cắt cứng theo số ký tự. Với mỗi mức tách, các phần nhỏ liền kề được gom lại đến gần `chunk_size` để tránh tạo ra quá nhiều chunk quá ngắn. Trường hợp cơ sở là khi đoạn đã không dài hơn `chunk_size`; nếu hết separator thì cắt cứng để bảo đảm chunk vẫn có kích thước giới hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Tôi lưu dữ liệu trong một danh sách in-memory; mỗi `Document` được chuẩn hoá thành record gồm `id`, `content`, bản sao `metadata` và `embedding`. Khi thêm tài liệu, embedding được tạo từ nội dung; khi tìm kiếm, query cũng được embedding rồi tính dot product với embedding của từng record. Kết quả được sắp xếp giảm dần theo score và chỉ trả về tối đa `top_k`, không trả embedding để output gọn hơn.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi lọc metadata trước rồi mới similarity search, vì nếu search trước thì các kết quả không đúng điều kiện có thể chiếm hết các vị trí top-k. Hàm `delete_document` giữ lại các record có `metadata['doc_id']` khác id cần xoá, nên có thể xoá toàn bộ chunk thuộc cùng một tài liệu. Hàm trả về `True` khi có ít nhất một chunk đã bị xoá, ngược lại trả về `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tôi lấy các chunk top-k từ store, đánh số từng chunk dạng `[1]`, `[2]`, ... và thêm nguồn của chunk vào ngữ cảnh. Prompt yêu cầu LLM chỉ dùng ngữ cảnh đã cung cấp, không đoán khi thiếu thông tin và trích dẫn số chunk khi trả lời; sau đó prompt được gửi vào `llm_fn`. Nếu không có chunk phù hợp, agent trả thông báo ngay và không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```
![alt text](image-1.png)
**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
