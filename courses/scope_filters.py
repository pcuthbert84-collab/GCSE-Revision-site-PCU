"""Keep school science topic evidence tightly scoped to the selected skill.

School timetable blocks can mix several sciences. Never prompt Gemini to teach
all the other lines as if they were the student's selected lesson.
"""
import re

SCIENCES=("biology","chemistry","physics")

def selected_source(course,topic):
    text=str(topic.get("source","") or "")
    if course.get("name") not in ("Combined Science","Separate Sciences"):
        return text
    title=str(topic.get("title","") or "")
    match=re.search(r"\\b(Biology|Chemistry|Physics)\\s*:\\s*([^\\n]+)",title,re.I)
    if not match:
        return text
    science=match.group(1).casefold()
    skill=re.sub(r"\\s+"," ",match.group(2)).strip(" .,;:-")
    skill=re.sub(r"\\s+"," ",skill).casefold()
    # Treat only this precise line as evidence. Any unrelated Biology/
    # Chemistry/Physics line must be excluded, even from the same term.
    lines=[]
    for line in text.splitlines():
        item=re.match(r"^\\s*(Biology|Chemistry|Physics)\\s*:\\s*(.*)$",line,re.I)
        if item and item.group(1).casefold()==science:
            content=re.sub(r"\\s+"," ",item.group(2)).casefold().strip(" .,;:-")
            if content==skill or content.startswith(skill+" "):
                lines.append(line.strip())
    return "\\n".join(lines) if lines else match.group(0)
