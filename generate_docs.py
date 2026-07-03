import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def setup_fonts():
    """Register Tahoma font from Windows to support Thai characters."""
    tahoma_path = r"C:\Windows\Fonts\tahoma.ttf"
    tahomabd_path = r"C:\Windows\Fonts\tahomabd.ttf"
    
    if os.path.exists(tahoma_path) and os.path.exists(tahomabd_path):
        pdfmetrics.registerFont(TTFont("Tahoma", tahoma_path))
        pdfmetrics.registerFont(TTFont("Tahoma-Bold", tahomabd_path))
        return "Tahoma", "Tahoma-Bold"
    else:
        print("Warning: Tahoma fonts not found in C:\\Windows\\Fonts. Thai characters might not display correctly.")
        return "Helvetica", "Helvetica-Bold"

def create_pdf(filename, title, content_paragraphs, font_regular, font_bold):
    """Helper function to create a PDF with Thai support."""
    os.makedirs("documents", exist_ok=True)
    filepath = os.path.join("documents", filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'ThaiTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=15
    )
    
    body_style = ParagraphStyle(
        'ThaiBody',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=10
    )
    
    list_style = ParagraphStyle(
        'ThaiList',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=11,
        leading=16,
        leftIndent=20,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6
    )

    story = []
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 10))
    
    # Add content
    for item in content_paragraphs:
        if isinstance(item, list):
            # List items
            for bullet in item:
                story.append(Paragraph(f"• {bullet}", list_style))
            story.append(Spacer(1, 8))
        else:
            story.append(Paragraph(item, body_style))
            story.append(Spacer(1, 5))
            
    doc.build(story)
    print(f"Created PDF: {filepath}")

def main():
    font_regular, font_bold = setup_fonts()
    
    # 1. Vacation Leave Policy
    vacation_title = "นโยบายการลาพักร้อนประจำปี (Vacation Leave Policy)"
    vacation_content = [
        "บริษัทฯ ตระหนักถึงความสำคัญของการพักผ่อนและการรักษาสุขภาพของพนักงานทุกคน จึงได้กำหนดนโยบายและสิทธิ์การลาพักร้อนประจำปีไว้ดังต่อไปนี้:",
        "1. สิทธิ์การลาพักร้อนพื้นฐาน:",
        [
            "พนักงานประจำทุกคนมีสิทธิ์ลาพักร้อน (Vacation Leave) หลังจากผ่านการทดลองงาน (120 วัน)",
            "พนักงานที่มีอายุงาน 1 - 3 ปี: ได้รับสิทธิ์ลาพักร้อน 10 วันทำการต่อปี",
            "พนักงานที่มีอายุงาน 3 - 5 ปี: ได้รับสิทธิ์ลาพักร้อน 12 วันทำการต่อปี",
            "พนักงานที่มีอายุงาน 5 ปีขึ้นไป: ได้รับสิทธิ์ลาพักร้อน 15 วันทำการต่อปี"
        ],
        "2. ขั้นตอนการขออนุมัติการลาพักร้อน:",
        [
            "พนักงานต้องส่งคำขออนุมัติการลาผ่านระบบ HR Portal ล่วงหน้าอย่างน้อย 3 วันทำการ",
            "การลาพักร้อนตั้งแต่ 5 วันทำการติดต่อกันขึ้นไป ต้องส่งคำขออนุมัติล่วงหน้าอย่างน้อย 15 วันทำการ",
            "การอนุมัติวันลาขึ้นอยู่กับการพิจารณาและดุลยพินิจของหัวหน้างาน (Line Manager) โดยคำนึงถึงภาระงานในทีมเป็นสำคัญ"
        ],
        "3. การสะสมและการยกยอดวันลาพักร้อน:",
        [
            "พนักงานสามารถสะสมวันลาพักร้อนที่เหลือจากปีปัจจุบันไปใช้ในปีถัดไปได้ไม่เกิน 5 วันทำการ",
            "วันลาพักร้อนที่ยกยอดไปปีถัดไป จะต้องนำมาใช้ให้หมดภายในไตรมาสแรก (ภายในวันที่ 31 มีนาคม) ของปีถัดไปเท่านั้น หากเลยกำหนดจะถือว่าสละสิทธิ์และไม่มีการชดเชยเป็นเงินสด"
        ],
        "หมายเหตุ: สำหรับพนักงานที่ยังไม่ผ่านการทดลองงาน หากมีความจำเป็นต้องหยุดงาน สามารถขอลาโดยไม่รับค่าจ้าง (Leave Without Pay) ได้เป็นกรณีพิเศษตามการอนุมัติของหัวหน้างานและฝ่าย HR"
    ]
    create_pdf("vacation_policy.pdf", vacation_title, vacation_content, font_regular, font_bold)
    
    # 2. Internal Contacts
    contacts_title = "สมุดรายนามและเบอร์ติดต่อภายใน (Internal Department Contacts)"
    contacts_content = [
        "พนักงานสามารถติดต่อแผนกต่างๆ ภายในองค์กรเพื่อประสานงานหรือขอความช่วยเหลือได้ตามรายละเอียดเบอร์ติดต่อและช่องทางอีเมลต่อไปนี้:",
        "1. แผนกเทคโนโลยีสารสนเทศ (IT Support Helpdesk)",
        [
            "เบอร์ติดต่อภายใน: 1101",
            "อีเมล: it.support@company.com",
            "เวลาทำการ: 08:30 น. - 17:30 น. (จันทร์ - ศุกร์)",
            "ขอบเขตการช่วยเหลือ: ปัญหาคอมพิวเตอร์, การตั้งค่ารหัสผ่าน, การเข้าใช้งาน VPN, ปัญหาเครือข่ายอินเทอร์เน็ต และการขอยืมอุปกรณ์ไอที"
        ],
        "2. แผนกทรัพยากรบุคคล (HR Department)",
        [
            "เบอร์ติดต่อภายใน: 1201",
            "อีเมล: hr@company.com",
            "ขอบเขตการช่วยเหลือ: กฎการลาพักร้อน, นโยบายสวัสดิการพนักงาน, ประกันสุขภาพกลุ่ม, การประเมินผลงาน และการเบิกค่าใช้จ่ายในการฝึกอบรม"
        ],
        "3. แผนกบัญชีและการเงิน (Finance & Accounting)",
        [
            "เบอร์ติดต่อภายใน: 1301",
            "อีเมล: finance@company.com",
            "ขอบเขตการช่วยเหลือ: ปัญหาเกี่ยวกับสลิปเงินเดือน (Payslip), ภาษีเงินได้หัก ณ ที่จ่าย (50 ทวิ), การเคลมค่าใช้จ่ายในการเดินทาง และการยื่นเบิกใบเสร็จต่างๆ"
        ],
        "4. แผนกดูแลอาคารและสถานที่ (Office Admin & Facilities)",
        [
            "เบอร์ติดต่อภายใน: 1401",
            "อีเมล: admin@company.com",
            "ขอบเขตการช่วยเหลือ: การออกคีย์การ์ดพนักงานใหม่, สิทธิ์การจอดรถ, การจองห้องประชุมส่วนกลาง และการแจ้งซ่อมอุปกรณ์ชำรุดในสำนักงาน"
        ]
    ]
    create_pdf("internal_contacts.pdf", contacts_title, contacts_content, font_regular, font_bold)
    
    # 3. Sick & Personal Leave Policy
    sick_title = "นโยบายการลาป่วยและลากิจ (Sick & Personal Leave Policy)"
    sick_content = [
        "นโยบายการลาเพื่อกิจธุระส่วนตัวและการเจ็บป่วยมีผลบังคับใช้กับพนักงานประจำและพนักงานสัญญาจ้างทุกคน โดยแบ่งเงื่อนไขออกเป็นดังนี้:",
        "1. นโยบายการลาป่วย (Sick Leave):",
        [
            "พนักงานมีสิทธิ์ลาป่วยได้ตามที่เจ็บป่วยจริง โดยจะได้รับค่าจ้างปกติไม่เกิน 30 วันทำการต่อปีการทำงาน ตามกฎหมายแรงงาน",
            "กรณีลาป่วยติดต่อกันตั้งแต่ 3 วันทำการขึ้นไป พนักงานต้องนำส่งใบรับรองแพทย์แผนปัจจุบันที่ออกโดยสถานพยาบาลที่ได้รับการรับรองให้แก่ฝ่าย HR ในวันที่กลับมาทำงาน",
            "การแจ้งลาป่วย: พนักงานต้องโทรศัพท์หรือส่งข้อความแจ้งให้หัวหน้างาน (Line Manager) ทราบโดยเร็วที่สุดอย่างน้อย 30 นาทีก่อนเวลาเริ่มงาน หรือไม่เกินเวลา 09:00 น. ของวันทำการแรกที่เริ่มลา"
        ],
        "2. นโยบายการลากิจธุระอันจำเป็น (Personal Leave):",
        [
            "พนักงานมีสิทธิ์ลากิจเพื่อทำธุระอันจำเป็นได้ 6 วันทำการต่อปี โดยได้รับค่าจ้างปกติ",
            "ขอบเขตกิจธุระจำเป็น เช่น การติดต่อหน่วยงานราชการ, การจัดงานศพครอบครัวใกล้ชิด, การดูแลบิดามารดาหรือบุตรที่เจ็บป่วยรุนแรง",
            "การแจ้งลากิจ: พนักงานต้องส่งใบลาในระบบ HR Portal ล่วงหน้าอย่างน้อย 1 วันทำการ พร้อมระบุเหตุผลในการลา และต้องได้รับอนุมัติจากหัวหน้างานก่อนวันที่จะหยุดปฏิบัติงานจริงเสมอ"
        ],
        "การส่งหลักฐานและเอกสารประกอบ: ขอให้พนักงานทำด้วยความซื่อสัตย์สุจริต การปลอมแปลงใบรับรองแพทย์หรือการลากิจโดยไม่มีเหตุผลอันจำเป็นจริง ถือเป็นการทำผิดวินัยขั้นร้ายแรงตามนโยบายของบริษัทฯ"
    ]
    create_pdf("general_policy.pdf", sick_title, sick_content, font_regular, font_bold)

if __name__ == "__main__":
    main()
