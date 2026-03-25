import csv, re

filename='results-per-artifact.csv'

class Artifact:

    def __init__(self, ID, conf, year):
        self.ID = ID
        self.conf = conf
        self.year = year
        self.success = False
        self.candidate = False
        self.scripted = False
        self.reuseintended = False
        self.paperlink = False
        self.repolink = False
        self.truerepolink = False
        self.linkeval = False
        self.rtime = None
        self.package = dict()

    def setbadge(self, badge):
        self.badge = badge

    def setfound(self, found):
        self.found = found
        
    def setcomplete(self, complete):
        self.complete = complete

    def setcandidate(self, cand):
        self.candidate = cand

    def setoutcome(self, out):
        self.outcome = out

        
artifacts = dict()

try:
    pattern = r"(\d+)\s?([mh])"
    # Open the file in read mode ('r')
    with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
        # Create a DictReader object
        reader = csv.DictReader(csvfile)
        
        # Iterate over each row in the file
        for row in reader:
            # Access data using column names (keys)
            # Example: Accessing 'first_name' and 'last_name' columns
            
            ID = (row['Artifact ID'] + '-' + row['Conference']).strip()
            
            if ID == "-":
                continue

            conf = row['Conference'].split(' ')[0]
            try:
                year = row['Conference'].split(' ')[1]
            except Exception as e:
                pass
            

            artifacts[ID] = Artifact(ID,conf,year)
            
            badge = row['badge']
            artifacts[ID].setbadge(badge)
            found = row['artifact found']
            complete = row['artifact complete']
            
            artifacts[ID].setfound(found)
            artifacts[ID].setcomplete(complete == 'y')
            artifacts[ID].setoutcome(row['Outcome'].strip())
            cand = row['candidate']
            if 'y' in found and 'y' in complete and badge == 'R':
                artifacts[ID].setcandidate(cand == 'y')
                if cand != 'y':
                    print("NOT CAND:", artifacts[ID].outcome, ID)                    

            artifacts[ID].scripted = (row['install fully scripted'] == 'y')
            artifacts[ID].reuseintended = (row['built for reuse'] == 'y')
            if row['pointer to paper from artifact'].strip() != "" and row['pointer to artifact from paper'].strip() != "":
                  artifacts[ID].linkeval = True
                  
            artifacts[ID].paperlink = (row['pointer to paper from artifact'] == 'y')
            artifacts[ID].repolink = (row['pointer to artifact from paper'] != 'n')
            artifacts[ID].truerepolink = (row['pointer to artifact from paper'] == 'y')

            for string in ['docker image','docker build code','conda/mamba/Jupyter/pyenv','requirements.txt','bash scripts','rust scripts','go scripts']:
                if row[string] == 'y':
                    artifacts[ID].package[string] = True
            if row['other'].strip() != "":
                artifacts[ID].package['other'] = True
            
            if cand != 'y' and badge == 'R' and found.startswith('y') and complete.startswith('y'):
                pass

            elif cand == 'y':
                matches = re.findall(pattern, artifacts[ID].outcome)
                if len(matches) > 0 and not artifacts[ID].outcome.startswith('NO'):
                    
                    artifacts[ID].success = True
                    if matches[0][1].startswith('m'):
                        if int(matches[0][0]) <= 10:
                            artifacts[ID].rtime = 'e'                            
                        elif int(matches[0][0]) <= 30:
                            artifacts[ID].rtime = 'm'
                        else:
                            artifacts[ID].rtime = 'h'
                    else:
                        artifacts[ID].rtime = 'h'



                
except FileNotFoundError:
    print(f"Error: The file '{filename}' was not found.")





conf = dict()
runs = dict()
ccand = dict()
links = plinks = rlinks = trlinks = 0
stats = dict()
docker = 0
python = 0
rust = 0
go = 0
bash = 0
other = 0
rdocker = 0
rpython = 0
rrust = 0
rgo = 0
rbash = 0
rother = 0
packages = dict()
rpackages = dict()

for venue in ['PETS2025', 'PETS2020', 'ACSAC2024', 'ACSAC2020']:
        stats[venue] = dict()
        repro = 0
        scripted = 0
        reuseintended = 0
        foundfirst = 0
        foundeventually = 0
        complete = 0
        cand = 0
        succ = 0
        plinks = 0
        rlinks = 0
        trlinks = 0
        easy = 0
        mod = 0
        hard = 0
        
        for (k,a) in artifacts.items():
            c = a.conf + a.year
            if c != venue:
                continue

        
            if a.badge != 'R':
                continue
            repro += 1
            
            if a.found == 'y':
                foundfirst += 1
            else:
                if a.found.startswith('y'):
                    foundeventually += 1
                else:
                    continue
            
            if a.complete:
                complete += 1
            else:
                continue
                
            if a.candidate:
                cand += 1
            else:
                continue

            n = len(a.package.keys())
            if n not in packages:
                packages[n] = 0
                rpackages[n] = 0
            if a.success:
                rpackages[n] += 1
            packages[n] += 1
            
            for string in ['docker image','docker build code','conda/mamba/Jupyter/pyenv','requirements.txt','bash scripts','rust scripts','go scripts','other']:
                if string in a.package:
                    if "docker" in string:
                        docker += 1
                        if a.success:
                            rdocker += 1
                    elif "requirements" in string or "conda" in string:
                        python += 1
                        if a.success:
                            rpython += 1
                    elif "rust" in string:
                        rust += 1
                        if a.success:
                            rrust += 1
                    elif "go" in string:
                        go += 1
                        if a.success:
                            rgo += 1
                    elif "bash" in string:
                        bash += 1
                        if a.success:
                            rbash += 1
                    else:
                        other += 1
                        if a.success:
                            rother += 1
                
            if a.scripted:
                scripted += 1
                
            if a.reuseintended:
                reuseintended += 1
            
            if a.success:
                succ += 1
                if a.rtime == 'e':
                    easy += 1
                elif a.rtime == 'm':
                    mod += 1
                else:
                    hard += 1
                
            if a.paperlink:
                plinks += 1
            if a.repolink: 
                rlinks += 1
            if a.truerepolink:
                trlinks += 1

        stats[venue]['reproduced'] = repro
        stats[venue]['foundfirst'] = foundfirst
        stats[venue]['foundadd'] = foundeventually
        stats[venue]['found'] = foundfirst + foundeventually
        stats[venue]['complete'] = complete
        stats[venue]['cand'] = cand
        stats[venue]['reused'] = succ
        stats[venue]['easy'] = easy
        stats[venue]['moderate'] = mod
        stats[venue]['hard'] = hard
        stats[venue]['scripted'] = scripted
        stats[venue]['reuseintended'] = reuseintended
        stats[venue]['plinks'] = plinks
        stats[venue]['rlinks'] = rlinks
        stats[venue]['trlinks'] = trlinks

mapping = dict()
mapping['reproduced'] = "RR"
mapping['found'] = "found (original+alternative)"
mapping['cand'] = "candidate"
mapping['reuseintended'] = "reuse-intended"
mapping['reuseintended'] = "reuse-intended"
mapping['plinks'] = "paper-link-in-art"
mapping['rlinks'] = "art-link-in-paper (correct + different)"

print("metric/venue", end="&")
for venue in ['PETS2025', 'PETS2020', 'ACSAC2024', 'ACSAC2020']:
    print(venue, end="&")    
print("total \\\\ \\hline")
for string in ['reproduced', 'found', 'complete', 'cand', 'reused', 'easy', 'moderate', 'hard', 'scripted', 'reuseintended', 'plinks', 'rlinks']:
    if string in mapping:
        print(mapping[string], end = " & ")
    else:
        print(string, end = " & ")
    all = 0
    for venue in ['PETS2025', 'PETS2020', 'ACSAC2024', 'ACSAC2020']:
        if string == 'found' and stats[venue]['foundadd'] > 0:
            print(str(stats[venue][string]) + " (" + str(stats[venue]['foundfirst'])+"+"+str(stats[venue]['foundadd'])+")", end = " & ")
        elif string == 'rlinks' and stats[venue]['trlinks'] < stats[venue]['rlinks']:
            diff = stats[venue]['rlinks'] - stats[venue]['trlinks']
            print(str(stats[venue][string]) + " (" + str(stats[venue]['trlinks'])+"+"+str(diff)+")", end = " & ")
        else:
            print(stats[venue][string], end = " & ")
        all += stats[venue][string]
    print(all, " \\\\")

print("Docker", docker, "reused", rdocker)
print("Python", python, "reused", rpython)
print("Rust", rust, "reused", rrust)
print("Go", go, "reused", rgo)
print("Bash", bash, "reused", rbash)
print("Other", other, "reused", rother)
for n in sorted(packages.keys()):
    print(packages[n], "artifacts were packaged", n, "way, reused", rpackages[n])
