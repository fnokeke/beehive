import random


def get(group):
    quotes = get_pos_quotes() if int(group) == 1 else get_neg_quotes()
    random.shuffle(quotes)
    return quotes


def get_pos_quotes():
    return [
        #
        'Mujhe video ki quality bahut acchi lagi. Isse doordarshan par dikhaya jaana chahiye. Video banane walon ne bahut accha video banaya hai.',
        #
        'Agar swasthya sambandhi vishay par video banana ho, toh aisa video hi banana chahiye. Yah video saari jaankari bahut hi jaldi aur prabhaavshaali tareeke se deta hai. Shaandaar video.',
        #
        'Mujhe video ki quality bahut acchi lagi. Inhone kai acche shots liye jaise ki panning, zooming, kandhe ke upar ka shot. Bahut Shaandaar!!',
        #
        'Yah video bahut acchi quality ka hai. Video banane walon ne bahut shaandaar video banaya hai. Mujhe video ki quality pasand aayi.',
        #
        'Mujhe video ko dekh kar bahut saari nayi jaankari mili jaise ki handpump ke paas ganda paani nahi ikattha hona chahiye. Swasthya sambandhi jaankaari acche se batayi gayi hai. Mujhe video pasand aayaa!',
        #
        'Actors ne health ke baare mein jarrori jaankaari dene ka kaam bahut sahi tarike se kiya hai. Shaandaar performance. Yah video bahut bahut accha laga.',
        #
        'Mujhe iss video ki kahaani bahut acchi lagi. Video dekh kar mazaa aa gaya. Bahut acchi jaankaari dene wala video dikhaya hai aapne.',
        #
        'Kya main iss video ko ek baar aur dekh sakta hoon!! Har second itna manoranzak tha!! Wakai, mein bahut badhiya video!!',
        #
        'Na keval yah video swasthya ki drashti se mahtvpoorna hai, bulki, yah video bahut manoranzak bhi hai. Aise video toh aur banane chahiye. Bahut upyogi jaankaari hai video mein.',
        #
        'Logon ko yah jaankaari milna bahut jaroori hai. Mujhe video mein dikhaayi gayi cheezein bahut acchi lagi. Health se judi aisi jaankaari milna logon ke liye bahut faaydemand hai.'
    ]


def get_neg_quotes():
    return [
        'Mujhe koi nayi jaankaari nahi mili. Video mein har baat baar baar bole jaaa rahe hain. Dimaag ka dahi ho gaya. Bekaar jaankaari.',
        #
        'Iss video ko koi bhi samajh nahi sakta. Message hi clear nahi hai. Yah video kisi ke kaam nahi aayega.',
        #
        'Bikul third class video hai. Bahut chhota hai lekin bahut confusing bhi hai. Video bananaa ek kalaa ke samaan hai aur yah video ek bekaar video ka udahran hai.',
        #
        'Kya ghatiya video hai. Kitni bekaar quality hai. Kaun dekhega aise pixelated video. Low quality!!',
        #
        'Video ki quality bahut kharaab hai. Video pixelated bhi hai. Video mein ek scene se doosre scene ka transition bhi kitna ajeeb sa hai!',
        #
        'Bahut hi bekaar actors hain video mein. Inko acting karna hi nahi aataa, dialogue bolna hi nahi aata. Inke chahre par koi bhaav hi nahi hain!!',
        #
        'Bahut hi bekaar production quality hai iss video ki. Kuch samajh hi nahi aa raha ki video mein kya ho raha hai. Iss video ko delete karo aur fir shuru se banao.',
        #
        'Mujhe toh yahi samajh nahi aaya ki yah video mujhe kyun dikhaya hai. Video bilkul bekaar aur boring hai. Jaankaari bhi bilkul confusing hai.',
        #
        'Iss video mein acchi acting toh chhodo, koi acting hi nahi kar raha. Actors ko training ki jaroorat hai. Inko acting karna aata hi nahi hai.',
        #
        'Video mein manoranjan ka naamo-nishaan nahi hai. Mujhe poora yakeen hai ki log aise video ko dekhenge hi nahi. Zero entertainment.'
    ]
