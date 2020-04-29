#!/usr/bin/python3
import sys
import os.path
import PDUclass

def main():
    env = {}
    while 1:
        line = sys.stdin.readline().strip()
        if line == '':
            break
        if type(line) is bytes: line = line.decode('utf8')
        key,data = line.split(':')
        env[key.strip()] = data.strip()
    sys.stdout.write("GET VARIABLE CMGR\n")
    sys.stdout.flush()
    line = sys.stdin.readline().strip()
    
    if  not "200 result=1" in line : return
    #sys.stdout.write("VERBOSE {}\n".format(line[-10:]))
    #sys.stdout.flush()
    
    if line[-1] == ')' : line = line[line.rfind(' '):]
    else : line = sys.stdin.readline().strip()
    
    pdus = []
    pdus.append(PDUclass.PDU(line[:-1]))
    
    # single sms
    if not pdus[0].mti_co.udhi: 
        opt = '\"asterisk,andy031968@404.city,' + 'SMS от {} >> {}\"'.format(env["agi_callerid"],pdus[0].ud.text)
        sys.stdout.write("EXEC JabberSend " + opt + "\n")
        sys.stdout.flush()
        return
    
    f_path = "/var/lib/asterisk/agi-bin/delme.txt"

    if os.path.exists(f_path):
        with open(f_path) as f: strs = f.readlines()
        for st in strs: 
            pdus.append(PDUclass.PDU(st[:-1]))

        pdus.sort(key=lambda x: (x.ud.udh.ieib.ied1, x.ud.udh.ieib.ied11, x.ud.udh.ieib.ied3))
        
        num = None # sms num
        num1 = None # sms num
        si = [0] # start index
        for i in range(len(pdus)):
            if (pdus[i].ud.udh.ieib.ied1 != num or pdus[i].ud.udh.ieib.ied11 != num1): # New SMS
                num = pdus[i].ud.udh.ieib.ied1
                num1 = pdus[i].ud.udh.ieib.ied11
                if not i : continue # Start
                si.append(i)
        si.append(None)

        npdus = [] 
        spdus = []
        for i in range(len(si)-1):
            if pdus[si[i]].ud.udh.ieib.ied2 > len(pdus[si[i]:si[i+1]]): 
                # SMS not completed
                npdus.extend(pdus[si[i]:si[i+1]])
            else: 
                # SMS completed 
                spdus.extend(pdus[si[i]:si[i+1]])
                sms_text = ''
                for spdu in spdus:
                    sms_text += spdu.ud.text
                opt = '\"asterisk,andy031968@404.city,' + 'SMS от {} >> {}\"'.format(env["agi_callerid"],sms_text)
                sys.stdout.write("EXEC JabberSend " + opt + "\n")
                sys.stdout.flush()
        if npdus :
            with open(f_path,'w') as f: 
                for npd in npdus: 
                    f.write(npd.line + '\n')
        else:
            os.unlink(f_path)
    else: 
        os.mkfifo(f_path)
        with open(f_path,'w') as f: 
            for pd in pdus: 
                f.write(pd.line + '\n')



main()