<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: ppt169

## communication
- primary_language: vi-VN
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
- body: 28
- title: 50
- subtitle: 38
- annotation: 22
- lead: 30
- footnote: 16
- code: 26
- display: 72

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
- mode: structured
- template_reuse_scope: layout
- template_adherence: adaptive

## pptx_masters
- presentation_core_master: Presentation Core

## pptx_layouts
- cover-expanded: presentation_core_master | Cover Expanded | P01
- schematic-title: presentation_core_master | Schematic Title | P02
- compare-proof: presentation_core_master | Compare Proof | P08
- three-columns: presentation_core_master | Three Columns | P11
- four-milestones: presentation_core_master | Four Milestones | P13
- closing-proof: presentation_core_master | Closing Proof | P15

## page_pptx_layouts
- P01: cover-expanded
- P02: schematic-title
- P03: schematic-title
- P04: schematic-title
- P05: schematic-title
- P06: schematic-title
- P07: schematic-title
- P08: compare-proof
- P09: schematic-title
- P10: schematic-title
- P11: three-columns
- P12: schematic-title
- P13: four-milestones
- P14: three-columns
- P15: closing-proof

## page_layouts
- P01: 01_title_slide
- P02: 06_title_only
- P03: 06_title_only
- P04: 06_title_only
- P05: 06_title_only
- P06: 06_title_only
- P07: 06_title_only
- P08: 05_comparison
- P09: 06_title_only
- P10: 06_title_only
- P11: 12_three_card
- P12: 06_title_only
- P13: 14_process_timeline
- P14: 12_three_card
- P15: 10_hero_statement

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
