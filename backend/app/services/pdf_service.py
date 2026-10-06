from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import mm
from datetime import datetime

def generate_pdf(report: dict) -> bytes:
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=15*mm,bottomMargin=15*mm)
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name='Cover',parent=styles['Title'],alignment=TA_CENTER,fontSize=26,spaceAfter=12)); styles.add(ParagraphStyle(name='Small',parent=styles['BodyText'],fontSize=8,leading=10))
    story=[Spacer(1,45*mm),Paragraph('STARTUPPILOT AI',styles['Cover']),Paragraph('AI-Generated Startup Business Plan',styles['Heading2']),Spacer(1,10*mm),Paragraph(report.get('startup_idea',''),styles['BodyText']),Spacer(1,6*mm),Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",styles['Small']),PageBreak()]
    def section(title): story.extend([Paragraph(title,styles['Heading1']),Spacer(1,3*mm)])
    section('Executive Summary'); story.append(Paragraph(report['marketing']['market_overview'],styles['BodyText']))
    section('Marketing Strategy')
    for key in ['target_audience','ideal_customer_profile','customer_pain_points','go_to_market_strategy','seo_keywords']:
        story.append(Paragraph(key.replace('_',' ').title(),styles['Heading3'])); story.append(Paragraph('<br/>'.join(map(str,report['marketing'].get(key,[]))),styles['BodyText']))
    section('Financial Plan'); story.append(Paragraph(report['finance']['executive_summary'],styles['BodyText']))
    rows=[['Month','Customers','Revenue','Expenses','Profit/Loss']]+[[str(x['month']),str(x['customers']),f"₹{x['revenue']:,.0f}",f"₹{x['total_expenses']:,.0f}",f"₹{x['profit_loss']:,.0f}"] for x in report['finance']['year1_projection']]
    t=Table(rows,repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#172033')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.25,colors.grey),('FONTSIZE',(0,0),(-1,-1),7)])); story.append(t)
    section('Product Requirements'); story.append(Paragraph(report['product']['product_overview'],styles['BodyText']))
    for x in report['product']['user_stories']: story.append(Paragraph('• '+x,styles['BodyText']))
    section('Validation Report'); v=report['validation']; story.append(Paragraph(f"Score: {v['overall_consistency_score']}/100 — {v['final_validation_status']}",styles['Heading2']))
    for k in ['verify_flags','contradictions','risky_assumptions','recommended_corrections']:
        story.append(Paragraph(k.replace('_',' ').title(),styles['Heading3'])); [story.append(Paragraph('• '+str(i),styles['BodyText'])) for i in v.get(k,[])]
    section('Sources & References')
    for s in report.get('sources',[]): story.append(Paragraph(f"{s.get('title','Source')} — {s.get('url','')}",styles['Small']))
    section('Assumptions & Disclaimer'); story.append(Paragraph('AI-generated estimates are illustrative and must be independently verified before financial or business decisions.',styles['BodyText']))
    doc.build(story); return buf.getvalue()
