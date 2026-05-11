import re
import hashlib
import os
from datetime import date
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.environ.get("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
SCRAPER_SECRET = os.environ.get("SCRAPER_SECRET", "")

RAW_TEXT = """Lesley Bustos
GB
•
6 reviews
3 days ago
Rated 5 out of 5 stars
An amazing experience and so happy with…
An amazing experience and so happy with the end results, good communication and understanding, worth the money and the time, very professional

Eliezer Rivera
NL
•
2 reviews
Apr 2, 2026
Rated 5 out of 5 stars
Esvita has been an amazing experience
Esvita has been an amazing experience. They are very professional, pay attention to detail and are very serviceable. They have excited my expectations. Their treatment is second to none. The accommodations were incredible, from the time they pick me up from the airport to the time they dropped me off. This is my second time with them and I would not think twice about doing any type of treatment with them.

Marita
MT
•
3 reviews
Mar 27, 2026
Rated 5 out of 5 stars
I am very very happy with what this…
I am very very happy with what this clinic has done. I love my smile after a long time. I would like to thank all the staff. They are awsome :))

Klontian Meta
GB
•
16 reviews
Mar 18, 2026
Rated 5 out of 5 stars
I honestly cannot recommend Esvita…
I honestly cannot recommend Esvita Clinic enough! My experience from start to finish has been absolutely amazing.
In just 3 days, they completely transformed my smile with high-quality dental implants, and I'm already so impressed with the results. The whole team is incredibly professional, friendly, and made me feel comfortable every step of the way. They explained everything clearly and took great care of me throughout the entire process.
Everything was so well organised, from the treatment to the overall experience, and the level of care and attention to detail is truly outstanding.
I'm currently in the healing stage and looking forward to completing everything 100%, but even now I feel so much more confident with my smile.
Thank you to everyone at Esvita Clinic for giving me my smile back – I highly recommend them to anyone considering dental work!

Jordan Ellwood
GB
•
1 review
Mar 18, 2026
Rated 5 out of 5 stars
Best teeth in Turkey
I had the best time at Esvita, they looked after me from the minute I landed in Istanbul until the minute I left, transfers was always on time and the dentist that did my procedure was the best! She designed my smile from scratch and it fits my mouth perfectly, I would recommend to anyone who is looking to use Esvita

Farid Lipi
DE
•
2 reviews
Mar 13, 2026
Rated 5 out of 5 stars
Just wanted to share my experience,
Just wanted to share my experience, The stuff was very kindly they took care of me very well, as a foreigner i was littebite scared with tranportation, but i didn't have to do anything by myself they will bring you from hotel to clinic and also to Airport. I would highly recommend it. Just had my first Hairplant surgery if everythings works well i will do the second session too. Wanted also mention Skyler and Liz for their kindly and hospilaty behaivour. The Full team is very friendly and Experienced. Thanks a lot

Miguel
PL
•
1 review
Mar 10, 2026
Rated 1 out of 5 stars
I had a hair transplant at this clinic…
I had a hair transplant at this clinic in 03.2025, with my main priority being the crown area. Despite clearly stating this before the procedure, the available grafts were distributed to other areas, including my frontal region, which I did not need. The result after a year is sparse crown density, far from what I expected.

Leah
GB
•
2 reviews
Feb 25, 2026
Rated 5 out of 5 stars
Had a lovely experience on my second…
Had a lovely experience on my second trip back to esvita, very happy with the result of my smile make over and I service I received, all transfers all taken care of and staff all very nice

David Santos
GB
•
5 reviews
Feb 24, 2026
Rated 5 out of 5 stars
Outstanding experience so far
Outstanding experience so far, professional and well-organised. I travelled for dental treatment and had 4 lower implants placed along with zirconia crowns on my front teeth. I am currently in the healing phase, but so far everything has gone very smoothly.

Finlay Dreha
GB
•
1 review
Feb 20, 2026
Rated 5 out of 5 stars
Great service!

Leanne
GB
•
6 reviews
Feb 20, 2026
Rated 5 out of 5 stars
Amazing experience very happy
I had been in contact with the clinic since 2025, they provided a lot of information including cost, duration and what options would like to be available for me. All I had to do was book flights, which cost around £260 return with luggage. The hotel was lovely and very comfortable and staff were very accommodating. Super happy with the results and I'll be back next year for some implant for my back teeth

Andre Strydom
NO
•
21 reviews
Feb 3, 2026
Rated 5 out of 5 stars
I felt like giving them all a big hug
I can't speak for everyone but I really loved these people. They were very friendly and nice. I felt like giving them all a big hug. The results yet remain to be seen because this is first day after operation but so far I'm very happy

Lee Hill
GB
•
8 reviews
Jan 31, 2026
Rated 5 out of 5 stars
A good experience from start to finish
A good experience from start to finish, arrived in Turkey and collected from airport and taken to hotel. Daily transfer to and from the hair clinic each day so no need to worry about getting around. Lovely staff who took care of everything along the way. Looking forward to seeing my new hair grow

Mariusz
PL
•
3 reviews
Jan 25, 2026
Rated 2 out of 5 stars
watch out !
watch out ! don't trust them. I arrived to the clinic but they took me to the other clinic, different name, different place. Esvita simple is selling acquired patients to other clinics. They trade you like an animal.

Pedro Luca
US
•
1 review
Jan 24, 2026
Rated 5 out of 5 stars
My experience here in turkey with…
My experience here in turkey with esvista was wonderful the staff took great care of me from the beginning to the end they were very helpful and professional I recommend anyone to this clinic for a new look for hair transplant.

Dyeimi Alex
NL
•
1 review
Jan 24, 2026
Rated 5 out of 5 stars
I've had a five star experience for my…
I've had a five star experience for my treatment at this clinic. Good communication and I was informed every step of the way everything I needed to know. They even provide food and drinks and all transfers to and from the hotel and the airport were taken care of too.

Michel Milovic
FR
•
1 review
Jan 20, 2026
Rated 1 out of 5 stars
Hair transplant
Hello, I underwent a hair transplant at this clinic, and I would like to express my deep disappointment with their professionalism and working methods. First of all, the hygiene conditions were completely unacceptable. Secondly, there was a serious issue regarding the price. An agreement had been made in advance for a hair transplant at a cost of 1800 euros. However, once I arrived at the clinic, the doctor demanded an additional 1000 euros. Furthermore, the result on the balding area is very unsatisfactory.

branden carrick
GB
•
1 review
Jan 13, 2026
Rated 5 out of 5 stars
Staff were incredibly helpful and…
Staff were incredibly helpful and friendly. Helped to answer all my questions and make me feel comfortable travelling all the way from Australia. Transport to and from airport and back from hotel to clinic was all organized and smooth. Overall the experience was incredible. Would highly recommend.

Abdulhakim Ezedin
GB
•
1 review
Jan 8, 2026
Rated 5 out of 5 stars
Hair transplant, esvita clinic
I came here for second transplant. Experience was nice. The doctors, nurses all seemed nice and caring. Thankyou all.

Card player music (ierapetra)
GB
•
5 reviews
Dec 27, 2025
Rated 5 out of 5 stars
I recommend to everyone they are…
I recommend to everyone they are professional and they do good job!!!

M. Abubakkar
GB
•
17 reviews
Dec 27, 2025
Rated 5 out of 5 stars
I had the pleasure of visiting this…
I had the pleasure of visiting this clinic for my transplant treatment. Conversations initially began just over a month ago with Chris, an extremely helpful individual who guided me throughout the entire process before my arrival. Upon arrival, Darina was present to guide me throughout the day. She was extremely pleasant to deal with, she explained everything clearly. Overall the process was smooth, and Chris and Darina made my visit worth it. I would highly recommend their services

Albert Arnold
BE
•
3 reviews
Dec 26, 2025
Rated 5 out of 5 stars
Love Yourself Forever
Love Yourself Forever. Dear Esvita Team, Thank you for being a source of inspiration, strength, and positivity. Your dedication, creativity, and teamwork truly make a difference, and it shows in everything you do. Big thanks the best medical advisor Lisa, and my coordinator Louise

Cddnn
GB
•
4 reviews
Dec 26, 2025
Rated 5 out of 5 stars
Whole process has been amazing
Whole process has been amazing, I am in love with my new teeth ! Nelly was so good coordinating everything and making sure things run smoothly for me ! The Dentist, he was amazing, knew what I wanted and delivered! Do not hesitate, to come to Esvita.

Shaun Owens
GB
•
9 reviews
Dec 26, 2025
Rated 5 out of 5 stars
From initial first contact my…
From initial first contact my experience as been above and beyond. everything has been explained in detail step by step. Upon arriving at the clinic I was greeted by Sonia the patient coordinator who went above and beyond exceptional. Everything was explained in great detail which made me feel at ease. I was treated by mustapha who was amazing dentist gentle and calm. I would always recommend esvita clinic they went above and beyond thank you so so much

Courtney Hickman
GB
•
1 review
Dec 17, 2025
Rated 5 out of 5 stars
Esvita Clinic has been amazing from the…
Esvita Clinic has been amazing from the start to end, I came across them on Instagram decided to message them for a consultation and 4 weeks later I was in Istanbul. I had 6 root canals, 22 crowns and minimum pain and my teeth look absolutely perfect.

Nicholas millar
GB
•
2 reviews
Dec 18, 2025
Rated 5 out of 5 stars
Absolutely fantastic from collection to…
Absolutely fantastic from collection to finish. 100% happy with the outcome. Nelly Bobby and mustafa were amazing and all the dental nurses. Thank-you so much for giving me my smile back.

customer
TR
•
1 review
Dec 4, 2025
Rated 5 out of 5 stars
From the moment I got of the plane and…
From the moment I got of the plane and I got picked up from esvita clinic everything has been spot on I have no bad words to say about them they have been excellent and they have stuck to there words everything they have said they have followed through with an they have explained everything in detail and helped me understand everything and I'm so happy with my new smile

Giovanni S. T
GB
•
1 review
Dec 4, 2025
Rated 5 out of 5 stars
I liked the staff
I liked the staff, and the crown I got I'm waiting it for it to set in they fulfilled my request of getting rid of my old gap.

Connor Stokes
GB
•
5 reviews
Dec 4, 2025
Rated 5 out of 5 stars
Alex is the best person to speak too
Alex is the best person to speak too! Top service from start to finish even when treatment is complete he's still there to answer questions. Really genuine guy and very helpful.

V M
MD
•
3 reviews
Dec 2, 2025
Rated 1 out of 5 stars
Avoid this clinic/Scammers
Avoid this clinic! Scammers, read 1 star reviews, on google also.

Charlene Kibble
GB
•
3 reviews
Dec 1, 2025
Rated 5 out of 5 stars
Implants
Highly recommend esvita, nelly was so warm and welcoming, the clinic was lovely and clean, staff were very professional. I hate the dentist but I can happily say I was in great hands and didn't feel a thing.

Milena
GB
•
4 reviews
Nov 28, 2025
Rated 5 out of 5 stars
My experience at Esvita clinic has been…
My experience at Esvita clinic has been amazing! The whole process was very smooth and efficient. I was in contact with Robert who guided me throughout the whole process. Once I had the treatment confirmed I was being looked after by Nelly who was honestly so amazing. My dentist Ervin who placed my veneers was so friendly, and was so patient with me. I got 20 emax veneers in BL1 and I am so happy with the result.

Simon
GB
•
12 reviews
Nov 27, 2025
Rated 1 out of 5 stars
Abysmal service.
I had a hair transplant with these and it was the worst 2000 pounds I've ever spent. I had the op in January 2023 and was guaranteed a full head of hair within a year and have never had even close to that. When I sent in pics of the failed transplant they blamed me for it not being a success.

Janis Lescinskis
LV
•
1 review
Nov 26, 2025
Rated 5 out of 5 stars
I'm very happy with my new smile
I'm very happy with my new smile. Thanks Esvita clinic!!

Shohail Choudhury
GB
•
9 reviews
Nov 25, 2025
Rated 5 out of 5 stars
My hair transplant journey was fantastic
My hair transplant journey gone fantastic with Esvita. The process was very smooth and professional. From airport to hotel to clinic and through all the steps of operation it was nicely explained and answered by professionals.

Kirsten Mclennan
GB
•
3 reviews
Nov 22, 2025
Rated 5 out of 5 stars
I came to esvita to have a whole new…
I came to esvita to have a whole new smile created. I'm so over the moon with my results. My dentist took extra care when working with me as he knew I was super anxious from the start.

Paige gilvesy
TR
•
1 review
Nov 21, 2025
Rated 5 out of 5 stars
I had an amazing experience with Esvita…
I had an amazing experience with Esvita clinic. I was involved in a sports accident resulting in some broken teeth and they made my smile perfect again. Alex, Louise and Martin were all amazing communicators and made me feel at ease answering all questions I had!

customer
TR
•
2 reviews
Nov 21, 2025
Rated 5 out of 5 stars
Everything

customer
PL
•
1 review
Nov 13, 2025
Rated 5 out of 5 stars
Absolutely fantastic
Absolutely fantastic, great experience, brilliant staff, highly recommend, life changing results

Adiposcience
GB
•
2 reviews
Nov 13, 2025
Rated 5 out of 5 stars
Turned my frown upside down
Recently back from Esvita after having 19 crowns and 4 root canals. After a tricky start istanbuls crazy traffic meant I had to wait a while for the transfer, the actual dental team and in-house team did an amazing job of making sure everything went as smooth as possible. Huge credit to Husam and Nelly who made sure everything went well. I'm absolutely over the moon with the final result.

Tomasz
TR
•
1 review
Nov 12, 2025
Rated 5 out of 5 stars
It was great and amaizing

Miroslaw
GB
•
1 review
Nov 12, 2025
Rated 5 out of 5 stars
It was great

Ireneusz
GB
•
11 reviews
Nov 12, 2025
Rated 5 out of 5 stars
Amazing
God. Those women so hot. No need for painkillers haha. Friendly and helpfull....

Naomi moran
TR
•
1 review
Nov 7, 2025
Rated 5 out of 5 stars
Would definitely recommend
Couldn't fault Esvita, best experience everrr! Would definitely recommend. Whole team welcoming and friendly and made you feel at ease throughout treatment.

Mr Gaetano Dileo
GB
•
3 reviews
Nov 7, 2025
Rated 5 out of 5 stars
Great set up great people great job

Khem Joshi
GB
•
16 reviews
Dec 11, 2025
Rated 5 out of 5 stars
Esvita is fantastic clinic.
Esvita is a fantastic clinic! I found Esvita through social media and came all the way from London for treatment. Hali, the medical advisor at Esvita Clinic, helped me with my hair transplant, and everything was perfectly organized. I highly recommend this clinic!

Chris McNair
GB
•
5 reviews
Oct 31, 2025
Rated 5 out of 5 stars
Looked after me from the minute I…
Looked after me from the minute I landed in instanbul. Very considerate of how I was feeling, knowing I was very nervous. Would highly recommend.

Ria Maria
AT
•
2 reviews
Oct 31, 2025
Rated 5 out of 5 stars
Hello to everyone!I'm Aaria from Austria
Hello to everyone! I'm Aaria from Austria. I would like to share my experiences with dental treatment and traveling to Istanbul. I came across one of the managers of the Esvita clinic, Hali, who promised that everything would be fine if I chose them. I'm very happy because I have most beautiful smile that give me so much happiness. Thank you esvita thank you guys.

customer
TR
•
1 review
Oct 25, 2025
Rated 5 out of 5 stars
I really apreciat the work and the…
I really apreciat the work and the deligation of the whole team here, i am in love with My teeth i feel very confident when i smile. A special shout out to Martin also he has been so nice to us from the very beginning. Highly recommend.

Customer
GB
•
2 reviews
Oct 18, 2025
Rated 5 out of 5 stars
Best choice ive ever made
Great communication and made booking and arranging the trip very easy. I flew out in november 2024 for hair transplant and have had better results than I could have imagined. Flew out again in October 2025 with my friend to have his hair done and decided to have my teeth whitened while here.

customer
TR
•
1 review
Oct 18, 2025
Rated 5 out of 5 stars
My experience was great was a little…
My experience was great was a little scared before coming over but they made me feel comfortable and got my smile up to the standard I wanted. Would really recommend this clinic to everyone.

Rhys Thomas
GB
•
2 reviews
Oct 18, 2025
Rated 5 out of 5 stars
Great experience
Great experience, very natural results, lisa my medical advisor was always at hand to answer any questions. Would definitely recommend.

customer
GB
•
5 reviews
Oct 17, 2025
Rated 5 out of 5 stars
Was very professional and trustworthy
Was very professional and trustworthy. However, I have to came back here for the final procedure.

Agbebaku Izobo
NG
•
2 reviews
Oct 17, 2025
Rated 5 out of 5 stars
Excellent customer service by the…
Excellent customer service by the medical advisor Liam, very responsive, Dentist was very professional, respectful and nice staffs. I love my new teeth!

mantas badinas
TR
•
1 review
Oct 14, 2025
Rated 5 out of 5 stars
I had a great experience at Esvita…
I had a great experience at Esvita Dental Clinic! The staff was amazing, very friendly and welcoming from the moment I walked in. The doctors were professional, careful, and took the time to explain everything clearly.

Alki Thomai
CY
•
2 reviews
Oct 8, 2025
Rated 5 out of 5 stars
Staff was amazing
Staff was amazing, everyone was super kind.

Lorna Stricklin
US
•
1 review
Oct 6, 2025
Rated 5 out of 5 stars
Esvita Dental Clinic
Esvita was actually in my top 3 choices and not number 1 prior to departure. Once in Istanbul, I toured the clinic, met the staff, and they won me over. This clinic utilizes emax materials along with the other state of the art technology and materials. I have a beautiful smile, healthy gums, and zero pain. I give them a 10 out of 10.

Andres Tarifa
GB
•
2 reviews
Oct 3, 2025
Rated 5 out of 5 stars
Amazing treatment,top quality service!
Amazing treatment, top quality service!! 0 pain and overall, i think is the best clinic choice I could have chosen!! Totally recommend it

Shannon
GB
•
1 review
Sep 29, 2025
Rated 5 out of 5 stars
Would highly recommend these have help…
Would highly recommend these have help me get the smile I've always wanted and couldn't have helped me any more than they have all the way through my journey such lovely staff and polite the clinic is also very clean and hygienic"""


def parse_reviews(text: str) -> list[dict]:
    reviews = []
    rating_pattern = re.compile(r'Rated (\d) out of 5 stars', re.IGNORECASE)
    matches = list(rating_pattern.finditer(text))
    noise = {'Useful', 'Share', 'Advertisement', 'Verified', '•',
             'See if a website is trustworthy without leaving the page',
             'Reply from Esvita Clinic'}

    for i, match in enumerate(matches):
        rating = int(match.group(1))
        start = matches[i-1].end() if i > 0 else 0
        before = text[start:match.start()].strip()
        before_lines = [l.strip() for l in before.split('\n') if l.strip()]

        name = 'Anonim'
        for line in reversed(before_lines):
            if (len(line) < 60 and line not in noise
                    and not re.match(r'^[A-Z]{2}$', line)
                    and not re.match(r'^\d+\s+reviews?$', line)
                    and not re.match(r'^(Updated\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d)', line)):
                name = line
                break

        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        after_lines = [l.strip() for l in text[match.end():end].split('\n')]
        text_lines = []
        for line in after_lines:
            if not line:
                if text_lines:
                    text_lines.append('')
                continue
            if line in noise or re.match(r'^\d+$', line):
                break
            if line.startswith('Reply from') or line.startswith('Esvita Clinic logo'):
                break
            text_lines.append(line)
        while text_lines and not text_lines[-1]:
            text_lines.pop()
        review_text = ' '.join(text_lines).strip()

        rid = hashlib.sha256(f"tp|{name}|{rating}".encode()).hexdigest()
        reviews.append({'review_id': rid, 'reviewer_name': name, 'rating': rating, 'review_text': review_text})

    seen = {}
    for r in reviews:
        if r['review_id'] not in seen or len(r['review_text']) > len(seen[r['review_id']]['review_text']):
            seen[r['review_id']] = r
    return list(seen.values())


async def post_to_api(reviews):
    today = date.today().isoformat()
    payload = {'reviews': reviews, 'snapshot_date': today, 'platform': 'trustpilot'}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{APP_URL}/api/scraper",
            json=payload,
            headers={'Authorization': f'Bearer {SCRAPER_SECRET}', 'Content-Type': 'application/json'},
            timeout=aiohttp.ClientTimeout(total=60),
        ) as resp:
            if resp.status != 200:
                raise Exception(f"API error {resp.status}: {await resp.text()}")
            return await resp.json()


async def main():
    reviews = parse_reviews(RAW_TEXT)
    print(f"Parsed {len(reviews)} reviews from paste")
    for r in reviews[:3]:
        print(f"  [{r['rating']}★] {r['reviewer_name']}: {r['review_text'][:60]}")
    result = await post_to_api(reviews)
    print(f"API: new={result.get('new')}, deleted={result.get('deleted')}, total={result.get('total')}")


asyncio.run(main())
