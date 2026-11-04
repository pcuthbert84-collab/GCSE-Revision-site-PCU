"""Pearson Edexcel International GCSE Mathematics A (4MA1), linear, Higher.
Topic labels are navigation summaries, not a reproduction of the specification.
Only enabled skill IDs can generate questions. All others are displayed as roadmap.
"""
COURSE = {
    "code": "4MA1", "name": "Mathematics A", "board": "Pearson Edexcel",
    "tier": "Higher", "papers": "1H and 2H, two hours and 100 marks each",
    "specification_url": "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-mathematics-a-2016.html",
}
TOPICS = {
 "1 Numbers and the number system": ["1.1 Integers", "1.2 Fractions", "1.3 Decimals", "1.4 Powers and roots", "1.5 Set language and notation", "1.6 Percentages", "1.7 Ratio and proportion", "1.8 Degree of accuracy", "1.9 Standard form", "1.10 Applying number", "1.11 Electronic calculators"],
 "2 Equations, formulae and identities": ["2.1 Use of symbols", "2.2 Algebraic manipulation", "2.3 Expressions and formulae", "2.4 Linear equations", "2.5 Proportion", "2.6 Simultaneous linear equations", "2.7 Quadratic equations", "2.8 Inequalities"],
 "3 Sequences, functions and graphs": ["3.1 Sequences", "3.2 Function notation", "3.3 Graphs", "3.4 Calculus"],
 "4 Geometry and trigonometry": ["4.1 Angles, lines and triangles", "4.2 Polygons", "4.3 Symmetry", "4.4 Measures", "4.5 Construction", "4.6 Circle properties", "4.7 Geometrical reasoning", "4.8 Trigonometry and Pythagoras' theorem", "4.9 Mensuration", "4.10 3D shapes and volume", "4.11 Similarity"],
 "5 Vectors and transformation geometry": ["5.1 Vectors", "5.2 Transformation geometry"],
 "6 Statistics and probability": ["6.1 Graphical representation of data", "6.2 Statistical measures", "6.3 Probability"],
}
SKILLS = {
 "2.7 Quadratic equations": [
  {"id":"quadratic_factorise", "name":"Solve monic quadratics by factorisation", "enabled":True, "spec_ref":"2.7 A"},
  {"id":"quadratic_formula", "name":"Solve quadratics using the quadratic formula", "enabled":True, "spec_ref":"2.7 B"},
  {"id":"quadratic_complete_square", "name":"Complete the square and solve", "enabled":False, "spec_ref":"2.7 B"},
  {"id":"quadratic_context", "name":"Form and solve contextual quadratic equations", "enabled":False, "spec_ref":"2.7 C"},
 ],
 "1.6 Percentages": [
  {"id":"percentage_change", "name":"Calculate percentage increase and decrease", "enabled":True, "spec_ref":"1.6"},
 ],
 "1.7 Ratio and proportion": [
  {"id":"ratio_share", "name":"Divide an amount in a given ratio", "enabled":True, "spec_ref":"1.7"},
 ],
}

def all_topics():
    return [topic for items in TOPICS.values() for topic in items]

def get_skill(skill_id):
    for topic, skills in SKILLS.items():
        for skill in skills:
            if skill["id"] == skill_id:
                return {**skill, "topic": topic}
    return None
