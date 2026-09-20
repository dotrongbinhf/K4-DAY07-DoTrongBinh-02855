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
| 1 | Đổi trả miễn phí 30 ngày | [Tiki](https://tiki.vn/thong-tin/tiki-doi-tra-de-dang-an-tam-mua-sam) | 2026-09-20 / not-stated | 246 | buyer, returns-policy, vi, Tiki |
| 2 | Chương trình đổi trả 365 | [Tiki](https://tiki.vn/blog/chuong-trinh-doi-tra-365/) | 2026-09-20 / 2023-11-10 | 875 | buyer, returns-policy, vi, Tiki |
| 3 | Hướng dẫn đổi trả bảo hành mô hình Dropship | [Tiki Học viện](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-dropship/) | 2026-09-20 / not-stated | 1,971 | seller, returns-warranty, vi, Tiki |
| 4 | Câu hỏi thường gặp đổi trả bảo hành | [Tiki Học viện](https://hocvien.tiki.vn/faq/cau-hoi-thuong-gap-ve-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 2,519 | seller, returns-warranty, vi, Tiki |
| 5 | Hướng dẫn đổi trả bảo hành mô hình FBT | [Tiki Học viện](https://hocvien.tiki.vn/faq/mo-hinh-fbt-huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh/) | 2026-09-20 / not-stated | 1,359 | seller, returns-warranty, vi, Tiki |
| 6 | Hướng dẫn đổi trả bồi thường mô hình NGON | [Tiki Học viện](https://hocvien.tiki.vn/faq/mo-hinh-ngon-huong-dan-quy-trinh-xu-ly-doi-tra-boi-thuong/) | 2026-09-20 / not-stated | 1,337 | seller, returns-compensation, vi, Tiki |
| 7 | Hướng dẫn đổi trả bảo hành mô hình SD | [Tiki Học viện](https://hocvien.tiki.vn/faq/huong-dan-quy-trinh-xu-ly-doi-tra-bao-hanh-mo-hinh-sd/) | 2026-09-20 / not-stated | 1,780 | seller, returns-warranty, vi, Tiki |
| 8 | Hướng dẫn theo dõi giao dịch RMA | [Tiki Học viện](https://hocvien.tiki.vn/faq/huong-dan-theo-doi-giao-dich-doi-tra-rma/) | 2026-09-20 / not-stated | 948 | seller, returns-process, vi, Tiki |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id`, `title` | string | `tiki-fbt-doi-tra-bao-hanh` | Định danh ổn định và giúp truy vết chunk về tài liệu gốc. |
| `source_url`, `retrieved_at`, `document_version` | string/date | URL chính thức, `2026-09-20`, `2026-08-21` hoặc `not-stated` | Kiểm tra provenance và độ mới của chính sách. |
| `audience` | enum | `buyer`, `seller`, `both` | Cho phép lọc đúng đối tượng; là trường bắt buộc cho benchmark K4-L3B. |
| `category` | string | `returns-policy`, `returns-warranty`, `returns-compensation` | Thu hẹp không gian tìm kiếm và phân biệt chính sách người mua với quy trình nhà bán. |
| `platform` | string | `Tiki` | Tránh trộn thời hạn/quy trình của nền tảng khác khi benchmark. |
| `language` | string | `vi` | Xác định ngôn ngữ của corpus và lựa chọn embedding phù hợp. |

### Phân biệt phần cá nhân và vai trò nhóm

Mỗi thành viên vẫn tự hoàn thiện toàn bộ phần code trong `src/`, tự chạy test và tự chạy benchmark với chiến lược riêng. Các role dưới đây là trách nhiệm điều phối/chia việc của nhóm, không thay thế phần code cá nhân.

| Role | Trách nhiệm nhóm | Phần cá nhân vẫn phải làm |
|------|------------------|---------------------------|
| R1 · Data | Đoàn Quang Thanh — kiểm tra nguồn, làm sạch tài liệu, metadata và `sources.csv`. | Tự hoàn thiện code và chạy benchmark với chiến lược riêng. |
| R2 · Benchmark | Đào Gia Bảo — chốt 5 query, gold answer và A/B metadata filter. | Tự hoàn thiện code và ghi kết quả retrieval của mình. |
| R3 · Strategy | Nguyễn Văn Thăng (2A202602835) — điều phối baseline; Đỗ Trọng Bình (2A202602855) — kiểm thử heading/section. | Tự hoàn thiện code và giải thích rationale chiến lược của mình. |
| R4 · Report/Demo | Đỗ Trọng Bình (2A202602855) — gom kết quả, chuẩn bị bảng so sánh và kịch bản demo. | Vẫn phải có chiến lược và báo cáo cá nhân riêng. |

Phân công nhóm chỉ là trách nhiệm tổng hợp; mỗi thành viên vẫn nộp phần cá nhân độc lập. Đoàn Quang Thanh chịu trách nhiệm tích hợp corpus Tiki và bản benchmark cuối trong thư mục gốc.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `tiki-doi-tra-365` | FixedSizeChunker (`fixed_size`) | 2 | 462.5 | Giữ đủ nội dung ngắn, nhưng có thể cắt giữa bullet. |
| `tiki-doi-tra-365` | SentenceChunker (`by_sentences`) | 3 | 290.3 | Giữ ranh giới câu/bullet tốt; đây là nguồn Q1. |
| `tiki-doi-tra-365` | RecursiveChunker (`recursive`) | 2 | 434.0 | Gộp được các đoạn ngắn, nhưng đôi khi trộn nhiều ý. |
| `tiki-dropship-doi-tra-bao-hanh` | FixedSizeChunker (`fixed_size`) | 5 | 434.2 | Ổn định, chunk chứa bằng chứng khá rõ. |
| `tiki-dropship-doi-tra-bao-hanh` | SentenceChunker (`by_sentences`) | 7 | 280.4 | Giữ section bằng chứng tốt, nhưng nhiều chunk nhỏ. |
| `tiki-dropship-doi-tra-bao-hanh` | RecursiveChunker (`recursive`) | 6 | 326.7 | Cân bằng giữa section và kích thước. |
| `tiki-ngon-doi-tra-boi-thuong` | FixedSizeChunker (`fixed_size`) | 3 | 479.0 | Ít chunk, nhưng section bồi thường có thể bị trộn. |
| `tiki-ngon-doi-tra-boi-thuong` | SentenceChunker (`by_sentences`) | 5 | 266.2 | Tách được quy trình và section bồi thường; phù hợp Q3 hơn. |
| `tiki-ngon-doi-tra-boi-thuong` | RecursiveChunker (`recursive`) | 4 | 332.0 | Giữ đoạn tự nhiên, nhưng semantic top-3 vẫn nhiễu. |

Các số liệu trên chạy với `chunk_size=500` và được tính trên phần nội dung sau front matter.

Trong benchmark Tiki, thành viên cá nhân dùng `SentenceChunker(max_sentences_per_chunk=3)` cùng embedding đa ngữ thật. Cách này đưa đúng chunk lên top-1 cho Q1, Q4, Q5 và đưa chunk gold của Q2 vào top-3; Q3 vẫn cần cải thiện bằng section-aware retrieval hoặc mở rộng chunk lân cận.

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Văn Thăng (2A202602835)**
- **Loại chiến lược:** `RecursiveChunker`, `chunk_size=700`, embedding Gemini `gemini-embedding-001`.
- **Mô tả & lý do chọn:** Recursive splitting ưu tiên các ranh giới section/đoạn trước khi cắt theo kích thước, phù hợp tài liệu chính sách có nhiều heading và bullet. Tham số 700 giúp giữ đủ ngữ cảnh cho các quy trình seller nhưng vẫn giới hạn kích thước chunk.
- **Kết quả:** 4/5 câu có ngữ cảnh liên quan trong top-3, tương đương 7/10 theo rubric. Q3 là lỗi chính: tìm đúng tài liệu NGON nhưng không đưa section có mốc 24 giờ và hồ sơ bồi thường vào top-3.

**Thành viên 2 — Đào Gia Bảo (2A202602793)**
- **Loại chiến lược:** `FixedSizeChunker`, `chunk_size=800`, `overlap=50`, `top_k=3`, embedding local `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều).
- **Mô tả & lý do chọn:** Fixed-size có overlap để giảm mất ngữ cảnh tại ranh giới chunk và tạo baseline ổn định trên cả tài liệu buyer lẫn seller. Đây là cấu hình độc lập với baseline 500 ký tự ở phần trên, nên được ghi riêng để tái lập đúng kết quả thành viên.
- **Kết quả:** 19 chunk trên 8 tài liệu; Q1, Q2, Q3 và Q5 có bằng chứng trả lời được, Q4 bị FAQ seller lấn át và thiếu chunk FBT. Điểm theo bảng trả lời của thành viên: 8/10.

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
- **Kết quả:** Bài cá nhân ghi nhận 3/5 câu có ngữ cảnh liên quan; quy đổi nghiêm ngặt theo rubric là 4/10 vì Q1/Q2 chỉ có context nhưng không đưa đủ bằng chứng lên top-1, Q5 đạt đủ, còn Q3/Q4 thất bại.

**Thành viên 4 — Đoàn Quang Thanh (2A202602841)**
- **Loại chiến lược:** `SentenceChunker`, tối đa 3 câu/chunk, embedding local `paraphrase-multilingual-MiniLM-L12-v2`.
- **Mô tả & lý do chọn:** Tách theo câu/bullet giúp các câu trả lời định lượng như “30 ngày”, “32 ngày” và “24 giờ” ít bị lẫn với nội dung bên cạnh. Chiến lược này cũng dễ kiểm tra bằng trích dẫn chunk và đã được chạy trên corpus Tiki cuối gồm 43 chunk.
- **Kết quả:** Q1, Q4, Q5 có chunk đúng ở top-1; Q2 có chunk gold ở top-2; Q3 vẫn chỉ đưa chunk NGON tổng quan lên top-3. Điểm theo rubric là 7/10.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Văn Thăng (2A202602835) | Recursive 700 + Gemini | 7 | Giữ section/đoạn dài, bao phủ tốt Q1/Q4/Q5 | Q3 bị nhiễu; raw score không so sánh trực tiếp với embedding local |
| Đào Gia Bảo | Fixed 800, overlap 50 + MiniLM | 8 | Bao phủ được Q1/Q2/Q3/Q5; overlap giảm mất context | Q4 bị FAQ lấn át; chunk-size lớn chưa đảm bảo đúng section |
| Đỗ Trọng Bình (2A202602855) | Heading-aware + recursive fallback | 4 | Giữ heading, dễ giải thích nguồn của chunk | Có chunk chỉ là heading; Q3/Q4 chưa lấy được bằng chứng chi tiết |
| Đoàn Quang Thanh | Sentence tối đa 3 câu + MiniLM | 7 | Top-1 tốt cho Q1/Q4/Q5, dễ tái lập và kiểm chứng | Q3 cần ghép section/lân cận hoặc rerank theo heading |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Với đúng bộ query hiện tại, Fixed 800/50 có điểm tổng hợp cao nhất theo benchmark thành viên (8/10), vì lấy được bằng chứng cho Q1, Q2, Q3 và Q5. Tuy nhiên đây không phải chiến thắng tuyệt đối: Sentence tốt hơn cho Q4 và cho các câu hỏi có đáp án ngắn ở top-1, còn Heading-aware giải thích section tốt nhưng cần cơ chế mở rộng chunk. Phương án triển khai phù hợp nhất là hybrid: sentence/section-aware chunking, metadata filter và mở rộng chunk lân cận trước khi trả lời.

| Ma trận điểm theo câu hỏi | Q1 | Q2 | Q3 | Q4 | Q5 | Tổng |
|---|---:|---:|---:|---:|---:|---:|
| Recursive 700 | 2 | 1 | 0 | 2 | 2 | 7/10 |
| Fixed 800/50 | 2 | 2 | 2 | 0 | 2 | 8/10 |
| Heading-aware | 1 | 1 | 0 | 0 | 2 | 4/10 |
| Sentence ≤3 câu | 2 | 1 | 0 | 2 | 2 | 7/10 |

> Ma trận trên là so sánh từng chiến lược độc lập. Nếu chọn kết quả tốt nhất của cả nhóm cho từng câu hỏi thì cả 5 câu đều có bằng chứng trong top-3 (10/10), nhưng đó là “ensemble/oracle theo câu hỏi”, không phải điểm của một pipeline duy nhất.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Chương trình đổi trả 365 ngày áp dụng cho ngành hàng và nhà bán nào? | Áp dụng cho ngành Điện gia dụng và Thiết bị số thuộc nhà bán Tiki Trading. | `tiki-doi-tra-365.md` — `## Phạm vi và thời điểm áp dụng` |
| 2 | Khi từ chối yêu cầu đổi trả hoặc bảo hành, nhà bán Dropship cần cung cấp những loại bằng chứng hợp lệ nào? | Biên bản bàn giao/đồng kiểm; ảnh hoặc video đóng gói/khui mở; hoặc biên bản thẩm định của hãng. | `tiki-dropship-doi-tra-bao-hanh.md` — `## Điều kiện và trách nhiệm` |
| 3 | Nhà bán mô hình NGON cần làm gì khi hàng hoàn bị hư hỏng do lỗi vận chuyển? | Liên hệ Tiki trong 24 giờ, xác nhận thông tin/giá trị bồi thường và cung cấp hồ sơ, chứng từ qua Seller Center. | `tiki-ngon-doi-tra-boi-thuong.md` — `## Khiếu nại và bồi thường hàng hoàn` |
| 4 | Nhà bán FBT phải sắp xếp rút hàng trong thời hạn bao lâu? | Trong 32 ngày làm việc kể từ khi phiếu trả hàng được tạo. | `tiki-fbt-doi-tra-bao-hanh.md` — `## Hàng đổi trả` |
| 5 | Thời hạn đổi trả miễn phí là bao lâu? *(chạy A/B với `metadata_filter={"audience": "buyer"}`)* | 30 ngày đổi trả miễn phí; nguồn cũng nêu cam kết hoàn 200% nếu hàng giả. | `tiki-doi-tra-30-ngay.md` — toàn bộ tài liệu |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Chương trình 365 ngày | Sentence | Có, top-1 `tiki-doi-tra-365#0` chứa đủ 3 gold terms | Lọc `buyer` vẫn giữ đúng tài liệu. |
| 2 | Bằng chứng Dropship | Fixed 800/50 | Có, benchmark thành viên đưa `tiki-dropship-doi-tra-bao-hanh#0` lên top-1; chunk section gold `#1` cũng nằm trong top-3 | Fixed xử lý tốt hơn Sentence ở câu này; cần kiểm tra nội dung chunk thay vì chỉ nhìn score. |
| 3 | Bồi thường NGON | Fixed 800/50 | Có, `tiki-ngon-doi-tra-boi-thuong#1` ở top-2 và chứa mốc 24 giờ/hồ sơ | Đây là câu mà overlap và chunk lớn giúp giữ đủ bằng chứng; Sentence/Recursive gốc còn bỏ sót section chi tiết. |
| 4 | Rút hàng FBT | Sentence | Có, top-1 `tiki-fbt-doi-tra-bao-hanh#2` chứa 32 ngày | Đáp án trực tiếp. |
| 5 | Đổi trả miễn phí 30 ngày | Sentence | Có, top-1 ở cả filtered và unfiltered | A/B cho thấy filter buyer không đổi thứ hạng trong corpus nhỏ. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Metadata filter giúp giới hạn đúng vai trò nhà bán/người mua và tránh trộn các chính sách buyer với quy trình seller. Với Q5, kết quả A/B không thay đổi vì tài liệu 30 ngày có điểm cao nhất trong cả hai trường hợp; tuy vậy filter vẫn là ràng buộc đúng theo schema và cần thiết khi corpus lớn hơn.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

- Không có một chiến lược thắng mọi câu hỏi: Fixed 800/50 có điểm tổng hợp cao nhất, Sentence mạnh ở các mốc thời gian ngắn, còn Heading-aware giúp truy vết section nhưng có thể trả về heading-only.
- Q3 là hard case quan trọng: điểm similarity của đúng tài liệu chưa đủ; hệ thống phải lấy đúng section “Khiếu nại và bồi thường” có các điều kiện 24 giờ, giá trị bồi thường và hồ sơ chứng từ.
- Metadata `audience` là tín hiệu kiểm soát phạm vi. Ở Q5, A/B không đổi top-1 vì corpus nhỏ, nhưng filter buyer vẫn loại các FAQ seller không phù hợp và sẽ có giá trị hơn khi corpus mở rộng.

**Kịch bản demo đề xuất:**

1. Mở `data/ecommerce/sources.csv` và cho thấy 8 tài liệu Tiki đều có `doc_id`, URL, `audience`, category, ngôn ngữ và ngày lấy.
2. Chạy benchmark Sentence ở thư mục gốc: `.venv/bin/python bench.py --provider local --strategy sentence --output ket_qua_benchmark_tiki.txt`; trình bày Q1, Q4, Q5 đúng ở top-1, Q2 đúng ở top-2 và Q3 là failure case.
3. Đối chiếu `tv2/benchmark.txt` để cho thấy Fixed 800/50 lấy được section chi tiết của Q3, sau đó chạy A/B Q5 với `metadata_filter={"audience": "buyer"}` và không filter.
4. Kết thúc bằng câu trả lời có trích dẫn `doc_id` + heading, không chỉ đọc điểm similarity; nêu cách cải thiện Q3 bằng adjacent-chunk expansion và rerank theo heading/evidence terms.

**Bài học rút ra khi so sánh trong nhóm:**
> Chunking thay đổi cả đơn vị ngữ nghĩa mà embedding nhìn thấy: chunk quá lớn giữ context nhưng dễ kéo theo nhiễu, chunk quá nhỏ giữ đáp án ngắn nhưng có thể tách heading khỏi bằng chứng. Vì các thành viên dùng cả Gemini và embedding local, nhóm không dùng raw similarity để kết luận hơn-kém; tiêu chí chính là gold evidence có vào top-3 và agent có trả lời đúng hay không. Kết quả cho thấy cách thực dụng nhất là kết hợp section/sentence boundary với metadata filter và adjacent-chunk expansion.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ lưu thêm `section_path`, `evidence_terms` và `effective_date` ở từng chunk, đồng thời tạo test bắt buộc cho các cụm “24 giờ”, “32 ngày”, “30 ngày”, “Tiki Trading” và ba loại bằng chứng Dropship. Khi truy xuất được heading nhưng thiếu bằng chứng, pipeline sẽ lấy thêm chunk trước/sau cùng section rồi rerank theo heading và từ khóa định lượng. Cuối cùng, nhóm sẽ cố định provider, model, chunk-size và top-k trong một file cấu hình chung để benchmark giữa thành viên hoàn toàn tái lập được.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 9 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **38 / 40** |
