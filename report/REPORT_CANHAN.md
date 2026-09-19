# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Võ Phú Hãn (2A202602628)
**Nhóm:** [Tên nhóm]
**Ngày:** 2026-09-19

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector nằm gần cùng hướng, nghĩa là hai đoạn văn có biểu diễn ngữ nghĩa tương đối giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên đăng ký học phần trong học kỳ.
- Câu B: Sinh viên ghi danh môn học trong kỳ.
- Tại sao tương đồng: Cùng nói về việc đăng ký môn học.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên đăng ký học phần trong học kỳ.
- Câu B: Thời tiết hôm nay nhiều mây.
- Tại sao khác: Hai câu nói về hai chủ đề không liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào hướng của vector nên phù hợp để so sánh nội dung, ít bị ảnh hưởng bởi độ dài văn bản hơn khoảng cách Euclid.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> `ceil((10000 - 50) / (500 - 50)) = ceil(22.11) = 23 chunks`.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap 100: `ceil((10000 - 100) / (500 - 100)) = 25 chunks`. Overlap lớn giúp giữ ngữ cảnh ở ranh giới giữa hai chunk, nhưng làm tăng số chunk và chi phí xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`HeadingSectionChunker.chunk`** — hướng tiếp cận cá nhân:
> Tách Markdown theo heading `#` đến `######`, nên mỗi chunk bắt đầu bằng tiêu đề Điều/Mục và phần nội dung ngay sau nó. Nếu một section dài quá `chunk_size=500`, phần thân được chia bằng `RecursiveChunker` và heading được lặp lại ở mỗi chunk con. Vì vậy kết quả truy xuất vẫn biết đoạn đó thuộc Điều/Mục nào, thay vì mất ngữ cảnh như cắt theo số ký tự.

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex nhận diện dấu `.`, `!`, `?` theo sau bởi khoảng trắng hoặc xuống dòng. Sau đó làm sạch khoảng trắng và gom tối đa số câu cấu hình trong mỗi chunk. Chuỗi rỗng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử các separator theo thứ tự ưu tiên, gom các phần còn trong `chunk_size` rồi đệ quy với phần quá dài. Base case là đoạn đã đủ ngắn hoặc không còn separator; khi đó cắt theo kích thước ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi document được chuẩn hóa thành record gồm id, content, metadata và embedding. Search embed query rồi xếp hạng các record theo dot product giảm dần.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Metadata được lọc trước khi tính similarity. Xóa dựa trên `metadata["doc_id"]`, loại toàn bộ chunk thuộc document đó và trả về có xóa được hay không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunk, ghép thành context có đánh dấu nguồn, rồi đưa context và câu hỏi vào prompt. Prompt yêu cầu chỉ trả lời dựa trên context và gọi `llm_fn` để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
42 passed in 0.06s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần trong học kỳ. | Sinh viên ghi danh môn học trong kỳ. | cao | -0.124371 | Không |
| 2 | Sinh viên đăng ký học phần trong học kỳ. | Thời tiết hôm nay nhiều mây. | thấp | -0.203438 | Có |
| 3 | Điểm trung bình được tính theo số tín chỉ. | Điểm trung bình học kỳ phụ thuộc vào số tín chỉ. | cao | -0.157722 | Không |
| 4 | Sinh viên phải tham dự kỳ thi đúng lịch. | Cán bộ coi thi kiểm tra danh sách phòng thi. | thấp | -0.181782 | Có |
| 5 | Văn bằng được cấp sau khi hoàn thành chương trình. | Con mèo đang ngủ trên ghế. | thấp | -0.130428 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là các câu gần nghĩa không luôn có score cao hơn câu không liên quan. Nguyên nhân là `_mock_embed` dùng vector giả lập xác định, nên chỉ phù hợp để test pipeline chứ không phản ánh semantic similarity thực tế.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Đánh giá retrieval |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Quy trình hoãn thi giữa kỳ cần thực hiện như thế nào? | Điều tổng hợp S1 — nộp đơn và minh chứng trong 03 ngày | 0,5956 | Có, rank 1 | Filter `audience=student` đưa gold chunk lên top-1 |
| 2 | Bộ phận nào của Trường sẽ xem xét các trường hợp có lí do chính đáng để vắng thi giữa kỳ? | Điều 11 — P.ĐTĐH xem xét | 0,7348 | Có, rank 2 | Chunk đúng tài liệu và chứa gold answer |
| 3 | Thời hạn lưu trữ đề thi các môn học hệ đại học chính quy của Trường là bao lâu? | Điều 21 — thời hạn 9 năm | 0,8010 | Có, rank 1 | Top-1 chứa gold answer |
| 4 | Sinh viên thuộc chương trình tài năng có các hình thức nào? | Điều 2 — chính thức và dự bị | 0,8022 | Có, rank 2 | Chunk đúng tài liệu và chứa gold answer |
| 5 | KLTN là viết tắt của cụm từ nào? | Điều 2 — KLTN: Khóa luận tốt nghiệp | 0,5559 | Có, rank 1 | Top-1 chứa gold answer |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 với HeadingSectionChunker

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> HeadingSectionChunker của tôi và RecursiveChunker của Minh Quân cùng đạt 5/5 trên corpus; SentenceChunker đạt 4/5. HeadingSectionChunker dễ kiểm tra hơn vì chunk luôn giữ tên Điều/Mục.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
