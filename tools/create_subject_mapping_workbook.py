"""Build DBSJP subject leader mapping workbook. No unverified claims auto-approved."""
import re
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from courses.v4_catalog import COURSES,topic_groups
from courses.subject_resource_atlas import qualification_reference,directory_resources

OUT=Path("DBSJP_Subject_Leader_Mapping_Workbook.xlsx")
NAVY="071D59"; RED="D50032"; WHITE="FFFFFF"; BLUE="EAF2FC"
YELLOW="FFF2CF"; GREY="F4F6FA"; GREEN="E1F3E7"; INK="24354C"
HEADERS=["Mapping ID","Year","Current DBSJP topic / block","Existing curriculum-map detail",
"School source","Taught?","Official spec section / point","Exact subtopic / skills",
"What students must know or be able to do","Teaching method / modelled example",
"Misconceptions / scaffolds / vocabulary","Question types and marks",
"What should earn marks / acceptable alternatives","Video lesson URL",
"Worksheet / quiz URL","Exam / practice question URL","Priority",
"Spec checked?","Links checked?","Review status","Reviewer","Reviewed date","Notes / corrections"]
CH=["Subject","Exam board","Code currently listed","Code correct?",
"Confirmed qualification and pathway","Exact papers / assessed components",
"Chosen History options / English texts / Geography case studies",
"Selected BTEC units / coursework / practical components",
"Tier, regional paper or entry series","Review status","Subject leader",
"Review date","Corrections / concerns","Official course page"]

def paint(cell,bg=WHITE,fg=INK,bold=False,size=10):
    cell.fill=PatternFill("solid",fgColor=bg)
    cell.font=Font(name="Aptos",size=size,bold=bold,color=fg)
    cell.alignment=Alignment(vertical="center",wrap_text=True)

def banner(ws,title,subtitle,last):
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=last)
    paint(ws.cell(1,1,title),NAVY,WHITE,True,17);ws.row_dimensions[1].height=42
    ws.merge_cells(start_row=2,start_column=1,end_row=2,end_column=last)
    paint(ws.cell(2,1,subtitle),GREY,INK);ws.row_dimensions[2].height=35
    ws.sheet_view.showGridLines=False

def dropdown(ws,column,choices,start=7,end=3000):
    v=DataValidation(type="list",formula1='"'+",".join(choices)+'"',allow_blank=True)
    v.showErrorMessage=True;v.error="Select an option from the list."
    ws.add_data_validation(v)
    c=letter(column);v.add(c+str(start)+":"+c+str(end))

def rows_for(name):
    allrows=[];seen=set()
    for group,items in topic_groups(name).items():
        for it in items:
            origin="School curriculum map" if it.get("kind")=="school" else "Booklet theme – confirm"
            key=(origin,it.get("year"),it.get("title","").casefold().strip(),
                 it.get("source","").casefold().strip()[:100])
            if key in seen:continue
            seen.add(key);allrows.append((it,origin))
    if not allrows:
        allrows=[({"title":"TOPIC TO ADD – department input required","source":"",
                   "year":None,"file":""},"Leader to complete")]
    return allrows

def subject_sheet(ws,name,course,items):
    banner(ws,"DBSJP  |  "+name,
           "Code in app: "+str(course.get("code") or "UNCONFIRMED")+
           "   •   Yellow cells need departmental input  •   Existing school detail is preserved",23)
    ws.merge_cells("A3:W3")
    paint(ws["A3"],GREY,RED,True);ws["A3"]="Required: taught? (F), spec point (G), exact skills (H–I), specification checked (R), approval (T), reviewer (U)."
    ws.row_dimensions[3].height=27
    ws.merge_cells("A4:W4")
    ws["A4"]="Add a new subtopic by duplicating its broad block row and giving its Mapping ID a distinct suffix (-A, -B). Do not invent official references."
    paint(ws["A4"],GREY,INK)
    for a,b,title,color in [(1,5,"EXISTING SCHOOL EVIDENCE",NAVY),
                            (6,9,"SPEC & COVERAGE", "176C70"),
                            (10,13,"HOW STUDENTS ARE TAUGHT / ASSESSED",RED),
                            (14,16,"DIRECT LEARNING RESOURCES",NAVY),
                            (17,23,"REVIEW & APPROVAL","176C70")]:
        ws.merge_cells(start_row=5,start_column=a,end_row=5,end_column=b)
        paint(ws.cell(5,a,title),color,WHITE,True)
    ws.row_dimensions[5].height=24
    for j,title in enumerate(HEADERS,1):
        paint(ws.cell(6,j,title),NAVY,WHITE,True)
    ws.row_dimensions[6].height=45
    for ix,(item,origin) in enumerate(items,1):
        row=ix+6
        values={1:re.sub("[^A-Z0-9]","",name.upper())[:9]+"-"+str(ix).zfill(4),
                2:("Y"+str(item.get("year"))) if item.get("year") else "Course",
                3:item.get("title",""),4:str(item.get("source",""))[:1900],
                5:item.get("file") or origin,6:"To confirm",
                17:"Medium",18:"Needs checking",19:"Not checked",20:"Not started"}
        for j in range(1,24):
            cell=ws.cell(row,j,values.get(j))
            paint(cell,(WHITE if row%2 else GREY) if j<=5 else YELLOW)
            if j==22:cell.number_format="dd mmm yyyy"
        ws.row_dimensions[row].height=53 if item.get("source") else 35
    widths=[18,13,43,55,29,17,34,37,47,47,44,37,47,42,42,43,
            14,19,18,20,23,19,48]
    for j,width in enumerate(widths,1):ws.column_dimensions[letter(j)].width=width
    dropdown(ws,6,["Yes","No","To confirm"])
    dropdown(ws,17,["High","Medium","Low"])
    dropdown(ws,18,["Yes","Needs checking","No"])
    dropdown(ws,19,["Checked","Not checked","Not applicable"])
    dropdown(ws,20,["Not started","In progress","Approved","Needs correction"])
    last=6+len(items);ws.auto_filter.ref="A6:W"+str(last);ws.freeze_panes="D7"
    ws.conditional_formatting.add("T7:T3000",
         FormulaRule(formula=['$T7="Approved"'],fill=PatternFill("solid",fgColor=GREEN)))
    ws.print_title_rows="1:6";ws.page_setup.orientation="landscape"
    return last

def course_confirm(ws):
    banner(ws,"DBSJP  |  Qualification Confirmation",
      "Each subject leader should confirm the current code, assessed route, chosen content and school-specific options before approving topic links.",14)
    ws.merge_cells("A4:N4");ws["A4"]="Yellow = confirm or amend. Existing code is NOT evidence that the examination route is fully verified."
    paint(ws["A4"],GREY,RED,True)
    for j,v in enumerate(CH,1):paint(ws.cell(6,j,v),NAVY,WHITE,True)
    ws.row_dimensions[6].height=42
    for i,(name,c) in enumerate(sorted(COURSES.items()),7):
        official=qualification_reference(c)
        values={1:name,2:c.get("board") or "Unconfirmed",3:c.get("code") or "Unconfirmed",
                4:"To confirm",10:"Not started",13:c.get("note",""),
                14:official["url"] if official else ""}
        for j in range(1,15):
            cell=ws.cell(i,j,values.get(j))
            paint(cell,BLUE if j in (1,2,3,14) else YELLOW)
            if j==12:cell.number_format="dd mmm yyyy"
        if official:
            ws.cell(i,14).hyperlink=official["url"]
            ws.cell(i,14).font=Font(name="Aptos",size=10,color="0563C1",underline="single")
        ws.row_dimensions[i].height=42
    for j,w in enumerate([31,27,19,18,36,45,49,46,36,19,25,18,50,65],1):
        ws.column_dimensions[letter(j)].width=w
    dropdown(ws,4,["Yes","No","To confirm"])
    dropdown(ws,10,["Not started","In progress","Approved","Needs correction"])
    ws.freeze_panes="D7";ws.auto_filter.ref="A6:N"+str(6+len(COURSES))

def dashboard(ws,sheetmap,counts):
    banner(ws,"DBSJP  |  Department Completion Dashboard",
           "Live counts are calculated from each department's Review status column.",9)
    hs=["Subject","Course code","Mapped rows","Approved","In progress",
        "Needs correction","Not started","% approved","Course status"]
    for j,h in enumerate(hs,1):paint(ws.cell(5,j,h),NAVY,WHITE,True)
    ws.row_dimensions[5].height=40
    for row,(name,c) in enumerate(sorted(COURSES.items()),6):
        tab=sheetmap[name].replace("'","''");n=counts[name];ending=6+n
        statusrange="'"+tab+"'!T7:T"+str(ending)
        vals={1:name,2:c.get("code") or "Unconfirmed",3:n,
              4:'=COUNTIF('+statusrange+',"Approved")',
              5:'=COUNTIF('+statusrange+',"In progress")',
              6:'=COUNTIF('+statusrange+',"Needs correction")',
              7:'=COUNTIF('+statusrange+',"Not started")',
              8:"=IF(C"+str(row)+"=0,0,D"+str(row)+"/C"+str(row)+")",
              9:"='COURSE CONFIRMATION'!J"+str(row+1)}
        for j in range(1,10):
            cell=ws.cell(row,j,vals.get(j));paint(cell,WHITE if row%2 else GREY)
            if j==8:cell.number_format="0%"
        ws.cell(row,1).hyperlink="#'"+tab+"'!A1"
        ws.cell(row,1).font=Font(name="Aptos",color="0563C1",underline="single",bold=True)
    total=6+len(COURSES)
    for j in (3,4,5,6,7):
        col=letter(j);ws.cell(total,j,"=SUM("+col+"6:"+col+str(total-1)+")")
    ws.cell(total,1,"TOTAL");ws.cell(total,8,"=IF(C"+str(total)+"=0,0,D"+str(total)+"/C"+str(total)+")")
    ws.cell(total,8).number_format="0%"
    for j in range(1,10):paint(ws.cell(total,j),NAVY,WHITE,True)
    for j,w in enumerate([34,18,19,16,17,20,17,18,22],1):ws.column_dimensions[letter(j)].width=w
    ws.freeze_panes="C6";ws.auto_filter.ref="A5:I"+str(total-1)

def instructions(ws):
    banner(ws,"DBSJP  |  Subject Leader Mapping Pack",
     "Complete the yellow fields, retain the existing school-map evidence and return the workbook for app integration.",5)
    steps=[
        ("1. COURSE CONFIRMATION","Check exam board, qualification code, papers, History options, English texts, BTEC units, tiers and coursework pathway."),
        ("2. YOUR SUBJECT TAB","Check every existing topic, marking 'Yes', 'No' or 'To confirm'. School-map entries are NOT automatically official specification points."),
        ("3. EXACT SPECIFICATION","Insert the published specification point/reference and write what students need to know and do. Leave unverified items as 'Needs checking'."),
        ("4. TEACHING KNOWLEDGE","Add useful model examples, scaffolds, misconceptions, vocabulary, question formats and acceptable alternative answers."),
        ("5. DIRECT RESOURCES","Add direct URLs to a video, a worksheet/quiz and a practice question where possible. Use RESOURCE IDEAS for suggestions, not automatic approval."),
        ("6. SIGN OFF","When checked, choose Approved, add reviewer and date; leave incomplete entries In progress or Needs correction."),
        ("7. RETURN THE FILE","Save the completed .xlsx and upload it here. I can transform the verified entries into an approved, auditable content library."),
        ("ADDING SUBTOPICS","If a block covers several specific skills, duplicate its row, give each new row an ID suffix -A/-B and complete a separate specification point."),
        ("IMPORTANT SAFEGUARD","Third-party links should not be copied wholesale into Gemini. Use original approved school explanations and respect publisher licensing.")
    ]
    ws.column_dimensions["A"].width=5;ws.column_dimensions["B"].width=33;ws.column_dimensions["C"].width=112
    for i,(title,detail) in enumerate(steps,4):
        paint(ws.cell(i,2,title),BLUE,NAVY,True)
        paint(ws.cell(i,3,detail),WHITE,INK)
        ws.row_dimensions[i].height=52
    ws.freeze_panes="B4"

def resources(ws):
    banner(ws,"DBSJP  |  Resource Ideas",
       "Existing resource directories from the app. These are starting points, not verified links for every exact specification subtopic.",5)
    for j,h in enumerate(["Subject","Provider / collection","Website","Notes","Approval state"],1):
        paint(ws.cell(5,j,h),NAVY,WHITE,True)
    row=6
    for name in sorted(COURSES):
        for item in directory_resources(name):
            vals=[name,item["title"],item["url"],item.get("note",""),"Directory – review"]
            for j,v in enumerate(vals,1):
                paint(ws.cell(row,j,v),WHITE if row%2 else GREY)
            ws.cell(row,3).hyperlink=item["url"]
            ws.cell(row,3).font=Font(name="Aptos",size=10,color="0563C1",underline="single")
            ws.row_dimensions[row].height=44;row+=1
    for j,w in enumerate([32,54,79,84,30],1):ws.column_dimensions[letter(j)].width=w
    ws.freeze_panes="C6";ws.auto_filter.ref="A5:E"+str(max(5,row-1))

def main():
    wb=Workbook();intro=wb.active;intro.title="START HERE"
    summary=wb.create_sheet("DASHBOARD");confirm=wb.create_sheet("COURSE CONFIRMATION")
    ideas=wb.create_sheet("RESOURCE IDEAS")
    names={};counts={}
    for name,c in sorted(COURSES.items()):
        tab=name[:31]
        if tab in wb.sheetnames:tab=name[:26]+"_"+str(len(names))
        ws=wb.create_sheet(tab)
        items=rows_for(name)
        subject_sheet(ws,name,c,items)
        ws.sheet_properties.tabColor=RED if "English" in name else NAVY
        names[name]=tab;counts[name]=len(items)
    instructions(intro);dashboard(summary,names,counts)
    course_confirm(confirm);resources(ideas)
    wb.properties.title="DBSJP Specification and Teaching Resource Mapping"
    wb.properties.description="For departmental review; codes and topics not automatically approved"
    wb.save(OUT)
    again=load_workbook(OUT,read_only=True)
    assert len(again.sheetnames)==len(COURSES)+4
    print("Built",OUT,"with",len(COURSES),"subject tabs and",sum(counts.values()),"prefilled topic/theme rows",OUT.stat().st_size,"bytes")

if __name__=="__main__":
    main()
