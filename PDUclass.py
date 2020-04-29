#!/usr/bin/python3
class PDU:
    line = None
    sca = None
    class MTI_CO: 
        mti = None
        mms = None
        sri = None
        udhi = None
        rp = None
        def __init__(self, bt):
            self.mms = bt & 4
            self.udhi = bt & 64
            #print("MIT {:08b}, MMS {:08b}, UDHI {:08b}".format(bt, self.mms, self.udhi))
    mti_co = None
    oa = None
    pid = None
    dsc = None
    scts = None
    udl = None
    class UD:
        class UDH:
            udhl = None
            class IEIB:
                iei = None
                iedl = None
                ied1 = None
                ied11 = None
                ied2 = None
                ied3 = None
                def __init__(self, bt):
                    self.iei = bt[0]
                    self.iedl = bt[1]
                    self.ied1 = bt[2]
                    cnt = 3
                    if (self.iedl == 4):
                        self.ied11 = bt[3]
                        cnt = 4
                    self.ied2 = bt[cnt]
                    self.ied3 = bt[cnt+1]
            ieib = None
            def __init__(self, bt):
                self.udhl = bt[0]
                self.ieib = self.IEIB(bt[1:])
        udh = None    
        text = None 
        def __init__(self, bt, udhi, dsc):
            if udhi : #long sms 
                if dsc: #UCS2
                    self.udh = self.UDH(bt)
                    self.text = bt[self.udh.udhl+1:].decode("utf-16-be")
            else:
                if dsc: #UCS2
                    self.text = bt.decode("utf-16-be")
    ud = None
    def __init__(self, ln):
        self.line = ln
        bt = bytes.fromhex(self.line)
        cnt = bt[0]+1
        self.mti_co = self.MTI_CO(bt[cnt])
        cnt += 1
        if (bt[cnt] % 2): cnt += bt[cnt] // 2  + 1 # Кол. байт
        else: cnt += bt[cnt] // 2
        cnt += 1 # байт - формат номера  
        # Pass PID
        cnt += 2
        self.dsc = bt[cnt]
        #print("DSC {:02X}".format(self.dsc))
        # Pass SCTS
        cnt += 8
        self.udl = bt[cnt]
        #print("UDL {:02X}".format(self.udl))
        cnt += 1 # Come to UD
        self.ud = self.UD(bt[cnt:],self.mti_co.udhi,self.dsc)

"""

def main():
    with open('raw_sms.txt') as f:
        strs = f.readlines()
    pdu = []
    for st in strs[1::2]:
        pdu.append(PDU(st))
        print(st)
        print(len(st))
    pdu.sort(key=lambda x: x.ud.udh.ieib.ied3)
    st = ""
    for pd in pdu:
        st += pd.ud.text.decode("utf-16-be")
    print(st)

main()
"""