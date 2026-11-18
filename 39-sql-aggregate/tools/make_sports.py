import random
random.seed(38)
sports=[(1,'수영'),(2,'헬스'),(3,'요가'),(4,'테니스'),(5,'필라테스')]
inst=[(1,'박서연','010-2101-3301',1),(2,'이도윤','010-2102-3302',1),(3,'김하준','010-2103-3303',2),(4,'최유나','010-2104-3304',3),
(5,'정민재','010-2105-3305',4),(6,'한지우','010-2106-3306',4),(7,'오세린','010-2107-3307',5),(8,'윤태호','010-2108-3308',1)]
courses=[(1,1,'수영 초급 아침반','초급','06:30',70000,20,1),(2,1,'수영 초급 저녁반','초급','19:00',70000,20,2),
(3,1,'수영 중급 새벽반','중급','06:00',80000,15,1),(4,1,'수영 고급반','고급','20:00',90000,12,2),
(5,1,'아쿠아로빅','초급','10:00',60000,25,None),(6,2,'헬스 PT 입문','초급','07:00',120000,10,3),
(7,2,'헬스 근력 중급','중급','18:30',100000,15,3),(8,3,'아침 요가','초급','08:00',65000,20,4),
(9,3,'요가 중급','중급','19:30',75000,18,4),(10,4,'테니스 입문','초급','09:00',90000,8,5),
(11,4,'테니스 중급 레슨','중급','07:30',110000,6,6),(12,4,'테니스 고급 레슨','고급','21:00',130000,6,6),
(13,5,'필라테스 기구 초급','초급','10:30',150000,8,7),(14,5,'필라테스 중급','중급','20:30',160000,8,7)]
names="김민준 이서윤 박도현 최지아 정하은 강시우 조서연 윤지호 장예린 임준서 한수아 오건우 서지민 신유찬 권나연 황민서 안태윤 송하린 류재원 전소율 홍승민 고은채 문지환 양다인 손현우 배서진 백준혁 허윤아 남궁민 노채원 하동건 곽미숙 차영호 주경자 우정희 구본철 민서영 진우성 엄하늘 채윤서".split()
regions=['영등포구']*12+['마포구']*11+['강서구']*10+['구로구']*7
random.shuffle(regions)
years=[1952,1955,1958,1960,1960,1961,1963,1965,1968,1970,1972,1974,1975,1978,1980,1981,1983,1985,1985,1987,1988,1990,1991,1993,1994,1995,1996,1997,1998,1999,2000,2000,2001,2002,2003,2004,2005,2006,2007,2008]
random.shuffle(years)
mem=[]
for i,n in enumerate(names,1):
    em=None if i%7==3 or i%11==5 else f"user{i:02d}@{'gmail.com' if i%3 else 'naver.com'}"
    ph=None if i%6==4 else f"010-{3000+i*37:04d}-{5000+i*53:04d}"
    mem.append((i,n,years[i-1],em,ph,regions[i-1]))
enr=[];eid=1
months=['2026-09','2026-10','2026-11']
fee={c[0]:c[5] for c in courses}
for mo in months:
    for c in courses:
        k=random.randint(2, max(3, c[6]//2))
        for m in random.sample(range(1,41),k):
            st='취소' if random.random()<0.1 else ('신청' if mo=='2026-11' else '완료')
            pay=0 if st=='취소' else fee[c[0]]
            enr.append((eid,m,c[0],mo,st,pay));eid+=1
q=lambda v:'NULL' if v is None else (str(v) if isinstance(v,int) else "'"+v+"'")
row=lambda t:'('+', '.join(q(v) for v in t)+')'
out=["DROP TABLE IF EXISTS enrollments, courses, instructors, members, sports;",
"CREATE TABLE sports (sport_id INTEGER PRIMARY KEY, sport_name VARCHAR(20) NOT NULL);",
"CREATE TABLE instructors (instructor_id INTEGER PRIMARY KEY, name VARCHAR(20) NOT NULL, phone VARCHAR(20), sport_id INTEGER REFERENCES sports (sport_id));",
"CREATE TABLE courses (course_id INTEGER PRIMARY KEY, sport_id INTEGER REFERENCES sports (sport_id), course_name VARCHAR(50) NOT NULL, level VARCHAR(10), start_time TIME, fee INTEGER, capacity INTEGER, instructor_id INTEGER REFERENCES instructors (instructor_id));",
"CREATE TABLE members (member_id INTEGER PRIMARY KEY, name VARCHAR(20) NOT NULL, birth_year INTEGER, email VARCHAR(100), phone VARCHAR(20), region VARCHAR(20));",
"CREATE TABLE enrollments (enrollment_id INTEGER PRIMARY KEY, member_id INTEGER REFERENCES members (member_id), course_id INTEGER REFERENCES courses (course_id), enroll_month VARCHAR(7), status VARCHAR(10), pay_amount INTEGER);"]
for t,rows in [('sports',sports),('instructors',inst),('courses',courses),('members',mem),('enrollments',enr)]:
    out.append(f"INSERT INTO {t} VALUES\n"+",\n".join(row(r) for r in rows)+";")
open('sports_center.sql','w').write("\n".join(out)+"\n")
print(len(enr))
