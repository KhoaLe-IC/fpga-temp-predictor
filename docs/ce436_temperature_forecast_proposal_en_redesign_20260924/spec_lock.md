<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: ppt169

## communication
- primary_language: en-US
- audience: Giảng viên CE436 và sinh viên, nhóm 3 người mới học DSP.
- objective: Giải thích đề xuất, cơ chế, kiểm chứng và kế hoạch để người nghe hiểu tính khả thi và thầy góp ý phạm vi, board, demo.
- core_message: Dự báo nhiệt độ +3 giờ bằng mô hình tuyến tính học offline trong C++, hiện thực fixed-point RTL trên FPGA.
- consumption_mode: balanced

## mode
- mode: custom
- mode_references: instructional
- mode_behavior: Theo một mẫu từ quá khứ qua mô hình, số cố định, FPGA và kiểm chứng, kết thúc bằng kế hoạch và góp ý.

## visual_style
- visual_style: custom
- visual_style_references: blueprint
- visual_style_behavior: Sơ đồ kỹ thuật trên nền trắng, vùng xám, nét chính xác, luồng trái sang phải; xanh đánh dấu mốc và nhánh trọng tâm, chú thích sát đối tượng.

## colors
- background: #FFFFFF
- secondary_bg: #F4F4F4
- primary: #0F62FE
- accent: #002D9C
- secondary_accent: #525252
- body_text: #161616
- secondary_text: #525252
- divider: #E0E0E0

## typography
- font_family: Arial
- title_family: Arial
- body_family: Arial
- code_family: Consolas
- body: 30
- title: 50
- subtitle: 38
- annotation: 24
- lead: 30
- footnote: 18
- code: 26
- display: 72
- technical_lead: 34
- visual_lead: 35
- metric_display: 45
- math_display: 47
- step_number: 53
- example_value: 42

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: tabler-outline/thermometer, tabler-outline/cpu, tabler-outline/database, tabler-outline/checklist

## page_rhythm
- P01: anchor
- P02: dense
- P03: dense
- P04: dense
- P05: dense
- P06: breathing
- P07: dense
- P08: dense
- P09: dense
- P10: dense
- P11: dense
- P12: dense
- P13: dense
- P14: dense
- P15: anchor

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
