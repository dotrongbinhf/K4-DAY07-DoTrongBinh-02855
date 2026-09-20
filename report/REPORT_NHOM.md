# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** FourGuys
**Thành viên:** Đoàn Quang Thanh (2A202602841), Nguyễn Văn Thăng (2A202602835), Đào Gia Bảo (2A202602793), Đỗ Trọng Bình (2A202602855)
**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách đổi trả, bảo hành và bồi thường của Tiki cho người mua và nhà bán.

**Tại sao nhóm chọn chủ đề này?**
> Đây là bộ chính sách Tiki có các mốc thời hạn, loại bằng chứng và quy trình riêng cho người mua, Dropship, FBT, NGON và SD. Metadata `audience` tách rõ `buyer`/`seller`, phù hợp để kiểm thử truy xuất theo đối tượng.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đổi trả miễn phí 30 ngày | [Tiki](https://tiki.vn/thong-tin/tiki-doi-tra-de-dang-an-tam-mua-sam) | 2026-09-20 / not-stated | 246 | buyer, returns-policy, vi |
| 2 | Chương trình đổi trả 365 | [Tiki](https://tiki.vn/blog/chuong-trinh-doi-tra-365/) | 2026-09-20 / 2023-11-10 | 875 | buyer, returns-policy, vi |
| 3 | Hướng dẫn đổi trả bảo hành mô hình Dropship | [Tiki Học viện](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-dropship/) | 2026-09-20 / not-stated | 2,052 | seller, returns-warranty, vi |
| 4 | Câu hỏi thường gặp đổi trả bảo hành | [Tiki Học viện](https://hocvien.tiki.vn/faq/cau-hoi-thuong-gap-ve-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 2,519 | seller, returns-warranty, vi |
| 5 | Hướng dẫn đổi trả bảo hành mô hình FBT | [Tiki Học viện](https://hocvien.tiki.vn/faq/mo-hinh-fbt-huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 1,359 | seller, returns-warranty, vi |
| 6 | Hướng dẫn đổi trả bồi thường mô hình NGON | [Tiki Học viện](https://hocvien.tiki.vn/faq/mo-hinh-ngon-huong-dan-quy-trinh-xu-ly-doi-tra-boi-thuong/) | 2026-09-20 / not-stated | 1,337 | seller, returns-compensation, vi |
| 7 | Hướng dẫn đổi trả bảo hành mô hình SD | [Tiki Học viện](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-sd/) | 2026-09-20 / not-stated | 1,780 | seller, returns-warranty, vi |
| 8 | Hướng dẫn theo dõi giao dịch RMA | [Tiki Học viện](https://hocvien.tiki.vn/faq/huong-dan-theo-doi-giao-dich-doi-tra-rma/) | 2026-09-20 / not-stated | 948 | seller, returns-process, vi |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------------------|
| `doc_id`, `title` | string | `tiki-fbt-doi-tra-bao-hanh` | Định danh ổn định và giúp truy vết chunk về tài liệu gốc. |
| `source_url`, `retrieved_at`, `document_version` | string/date | URL chính thức, `2026-09-20`, `not-stated` | Kiểm tra provenance và độ mới của chính sách. |
| `license_or_permission` | string | `public-source` | Căn cứ sử dụng dữ liệu công khai theo quy định lab. |
| `audience` | enum | `buyer`, `seller`, `both` | Cho phép lọc đúng đối tượng; trường bắt buộc cho benchmark K4-L3B. |
| `category` | string | `returns-policy`, `returns-warranty`, `returns-compensation` | Thu hẹp không gian tìm kiếm giữa chính sách người mua và quy trình nhà bán. |
| `language` | string | `vi` | Xác định ngôn ngữ của corpus và lựa chọn embedding phù hợp. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `tiki-doi-tra-365` | FixedSizeChunker (`fixed_size`) | 2 | 462.5 | Giữ đủ nội dung ngắn, nhưng có thể cắt giữa ý/câu. |
| `tiki-doi-tra-365` | SentenceChunker (`by_sentences`) | 3 | 290.3 | Giữ ranh giới câu tốt; đây là nguồn Q1 và Q5. |
| `tiki-doi-tra-365` | RecursiveChunker (`recursive`) | 2 | 434.0 | Gộp được các đoạn ngắn, nhưng đôi khi trộn nhiều ý. |
| `tiki-dropship-doi-tra-bao-hanh` | FixedSizeChunker (`fixed_size`) | 5 | 450.4 | Ổn định, chunk chứa bằng chứng khá rõ. |
| `tiki-dropship-doi-tra-bao-hanh` | SentenceChunker (`by_sentences`) | 7 | 292.0 | Giữ section bằng chứng tốt, ranh giới câu rõ ràng. |
| `tiki-dropship-doi-tra-bao-hanh` | RecursiveChunker (`recursive`) | 7 | 291.4 | Cân bằng giữa section và kích thước. |
| `tiki-ngon-doi-tra-boi-thuong` | FixedSizeChunker (`fixed_size`) | 3 | 479.0 | Ít chunk, nhưng section bồi thường có thể bị trộn. |
| `tiki-ngon-doi-tra-boi-thuong` | SentenceChunker (`by_sentences`) | 5 | 266.2 | Tách được quy trình và section bồi thường; phù hợp Q3 hơn. |
| `tiki-ngon-doi-tra-boi-thuong` | RecursiveChunker (`recursive`) | 4 | 332.0 | Giữ đoạn tự nhiên, nhưng semantic top-3 vẫn nhiễu. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Văn Thăng (2A202602835)**
- **Loại chiến lược:** `RecursiveChunker`, `chunk_size=700`, embedding Gemini `gemini-embedding-001`.
- **Mô tả & lý do chọn:** Recursive splitting ưu tiên các ranh giới section/đoạn trước khi cắt theo kích thước, phù hợp tài liệu chính sách có cấu trúc phân cấp heading và các đoạn quy định. Tham số 700 giúp giữ đủ ngữ cảnh cho các quy trình seller nhưng vẫn giới hạn kích thước chunk.

**Thành viên 2 — Đào Gia Bảo (2A202602793)**
- **Loại chiến lược:** `FixedSizeChunker`, `chunk_size=800`, `overlap=50`, `top_k=3`, embedding local `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều).
- **Mô tả & lý do chọn:** Fixed-size có overlap để giảm mất ngữ cảnh tại ranh giới chunk và tạo baseline ổn định trên cả tài liệu buyer lẫn seller. Đây là cấu hình độc lập với baseline 500 ký tự ở phần trên, nên được ghi riêng để tái lập đúng kết quả thành viên.

**Thành viên 3 — Đỗ Trọng Bình (2A202602855)**
- **Loại chiến lược:** `HeadingChunker` — tách theo heading Markdown, sau đó dùng recursive fallback cho section quá dài; 39 chunk.
- **Mô tả & lý do chọn:** Chính sách Tiki thường đặt đáp án dưới các heading như “Điều kiện và trách nhiệm” hoặc “Khiếu nại và bồi thường”, nên giữ heading cùng nội dung giúp truy vết section tốt hơn. Cách này vẫn có rủi ro tạo chunk chỉ chứa tiêu đề nếu section bị tách chưa đủ rộng.
- **Code snippet (pseudocode tương ứng với implementation cá nhân):**
```python
sections = split_by_markdown_heading(document)
chunks = []
for section in sections:
    chunks.extend(recursive_split(section) if too_long(section) else [section])
```

**Thành viên 4 — Đoàn Quang Thanh (2A202602841)**
- **Loại chiến lược:** `SentenceChunker`, tối đa 3 câu/chunk, embedding local `paraphrase-multilingual-MiniLM-L12-v2`.
- **Mô tả & lý do chọn:** Tách theo ranh giới câu giúp các câu trả lời định lượng như “30 ngày”, “32 ngày” và “24 giờ” ít bị lẫn với các điều khoản khác. Chiến lược này cũng dễ kiểm tra bằng trích dẫn chunk và đã được chạy trên corpus Tiki cuối gồm 43 chunk.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Văn Thăng (2A202602835) | Recursive 700 + Gemini | 7 | Giữ section/đoạn dài, bao phủ tốt Q1/Q4/Q5 | Q3 bị nhiễu; raw score không so sánh trực tiếp với embedding local |
| Đào Gia Bảo | Fixed 800, overlap 50 + MiniLM | 8 | Bao phủ được Q1/Q2/Q3/Q5; overlap giảm mất context | Q4 bị FAQ lấn át; chunk-size lớn chưa đảm bảo đúng section |
| Đỗ Trọng Bình (2A202602855) | Heading-aware + recursive fallback | 4 | Giữ heading, dễ giải thích nguồn của chunk | Có chunk chỉ là heading; Q3/Q4 chưa lấy được bằng chứng chi tiết |
| Đoàn Quang Thanh | Sentence tối đa 3 câu + MiniLM | 7 | Top-1 tốt cho Q1/Q4/Q5, dễ tái lập và kiểm chứng | Q3 cần ghép section/lân cận (đề xuất cải tiến) |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Với đúng bộ query hiện tại, Fixed 800/50 có điểm tổng hợp cao nhất theo benchmark thành viên (8/10), vì lấy được bằng chứng cho Q1, Q2, Q3 và Q5. Tuy nhiên đây không phải chiến thắng tuyệt đối: Sentence tốt hơn cho Q4 và cho các câu hỏi có đáp án ngắn ở top-1, còn Heading-aware giải thích section tốt nhưng cần cơ chế mở rộng chunk. Hướng đề xuất cải tiến (proposed improvement) cho tương lai là thử nghiệm kết hợp sentence/section-aware chunking với mở rộng ngữ cảnh lân cận trước khi trả lời.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Chương trình đổi trả 365 ngày áp dụng cho ngành hàng và nhà bán nào? | Áp dụng cho ngành Điện gia dụng và Thiết bị số thuộc nhà bán Tiki Trading. | `tiki-doi-tra-365.md` — `## Phạm vi và thời điểm áp dụng` |
| 2 | Khi từ chối yêu cầu đổi trả hoặc bảo hành, nhà bán Dropship cần cung cấp những loại bằng chứng hợp lệ nào? | Tài liệu chứng minh chất lượng/tiêu chuẩn/tính năng sản phẩm; biên bản bàn giao hoặc đồng kiểm với đơn vị vận chuyển; hoặc hình ảnh/video đóng gói/khui mở hàng hoàn. | `tiki-dropship-doi-tra-bao-hanh.md` — `## Điều kiện và trách nhiệm` |
| 3 | Nhà bán mô hình NGON cần làm gì khi hàng hoàn bị hư hỏng do lỗi vận chuyển? | Liên hệ Tiki trong 24 giờ, xác nhận thông tin/giá trị bồi thường và cung cấp hồ sơ, chứng từ qua Seller Center. | `tiki-ngon-doi-tra-boi-thuong.md` — `## Khiếu nại và bồi thường hàng hoàn` |
| 4 | Nhà bán FBT phải sắp xếp rút hàng trong thời hạn bao lâu? | Trong 32 ngày làm việc kể từ khi phiếu trả hàng được tạo. | `tiki-fbt-doi-tra-bao-hanh.md` — `## Hàng đổi trả` |
| 5 | Khách hàng cần cung cấp bằng chứng gì khi khiếu nại đổi trả? *(chạy A/B với `metadata_filter={"audience": "buyer"}`)* | Video mở kiện từ bên ngoài đến khi kiểm tra sản phẩm; ảnh sản phẩm lỗi; ảnh tem kiện hiển thị mã đơn; và ảnh tình trạng hộp/thùng cùng sản phẩm bên trong. | `tiki-doi-tra-365.md` — `## Ngoại lệ và bằng chứng` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Chương trình 365 ngày | Sentence | Có, top-1 `tiki-doi-tra-365#0` chứa đủ 3 gold terms | Lọc `buyer` giữ đúng tài liệu. |
| 2 | Bằng chứng Dropship | Fixed 800/50 | Có, benchmark thành viên đưa `tiki-dropship#0` lên top-1; ở Sentence chunking, chunk gold `#1` đứng hạng 2 (score 0.6634) | Cả hai chiến lược đều đưa bằng chứng vào top-3; Fixed đưa đúng doc lên top-1. |
| 3 | Bồi thường NGON | Fixed 800/50 | Có, `tiki-ngon-doi-tra-boi-thuong#1` ở top-2 và chứa mốc 24 giờ/hồ sơ | Overlap và chunk lớn của Fixed giữ đủ bằng chứng; Sentence gốc còn bỏ sót section chi tiết. |
| 4 | Rút hàng FBT | Sentence | Có, top-1 `tiki-fbt-doi-tra-bao-hanh#2` chứa 32 ngày | Đáp án trực tiếp. |
| 5 | Bằng chứng khiếu nại đổi trả | Sentence | Có khi có filter (`audience=buyer`), top-1 `tiki-doi-tra-365#2` (score 0.5621) | A/B cho thấy filter là điều kiện quyết định: nếu không filter, top-1 bị lấy nhầm sang tài liệu seller (`tiki-fbt#7`, score 0.6889). |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc metadata giúp ích quyết định ở câu hỏi 5 (bằng chứng khiếu nại đổi trả của khách hàng). Khi không lọc (`metadata_filter=None`), cả top-3 đều bị chiếm bởi tài liệu dành cho nhà bán (`seller`) do sự tương đồng từ khóa về khiếu nại đổi trả. Khi áp dụng bộ lọc `audience: "buyer"`, toàn bộ tài liệu nhà bán bị loại bỏ và đưa chính xác chunk bằng chứng của người mua lên top-1.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- Không có một chiến lược thắng mọi câu hỏi: Fixed 800/50 có điểm tổng hợp cao nhất, Sentence mạnh ở các mốc thời gian ngắn, còn Heading-aware giúp truy vết section nhưng có thể trả về heading-only.
- Q3 là hard case quan trọng: điểm similarity của đúng tài liệu chưa đủ; hệ thống phải lấy đúng section “Khiếu nại và bồi thường” có các điều kiện 24 giờ, giá trị bồi thường và hồ sơ chứng từ.
- Metadata `audience` là tín hiệu kiểm soát phạm vi bắt buộc. Ở Q5, nếu không có filter buyer thì toàn bộ top-3 bị chiếm bởi tài liệu seller do từ khóa khiếu nại của seller có điểm tương đồng cao hơn.

**Bài học rút ra khi so sánh trong nhóm:**
> Chunking thay đổi cả đơn vị ngữ nghĩa mà embedding nhìn thấy: chunk quá lớn giữ context nhưng dễ kéo theo nhiễu, chunk quá nhỏ giữ đáp án ngắn nhưng có thể tách heading khỏi bằng chứng. Vì các thành viên dùng cả Gemini và embedding local, nhóm không dùng raw similarity để kết luận hơn-kém; tiêu chí chính là gold evidence có vào top-3 và agent có trả lời đúng hay không.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm đề xuất các hướng thử nghiệm tiếp theo (proposed improvements): bổ sung `section_path` và `effective_date` vào metadata của từng chunk, đồng thời thử nghiệm cơ chế adjacent-chunk expansion để khi truy xuất được chunk gần đúng (như Q3), hệ thống lấy thêm chunk lân cận cùng `doc_id` nhằm hoàn chỉnh ngữ cảnh trước khi đưa vào prompt của agent.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **38 / 40** |
