import re
import hashlib
import os
import sys
from datetime import date

import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()

APP_URL = os.environ.get("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
SCRAPER_SECRET = os.environ.get("SCRAPER_SECRET", "")

# Paste the full Trustpilot review text below (between the triple-quotes)
RAW_TEXT = """Killian Lyons
IE
•
2 reviews
Sep 25, 2025
Rated 5 out of 5 stars
From the moment I landed
From the moment I landed, Esvita have been nothing short of amazing. Transport, hotel, treatment and people were all amazing. My treatment was complicated and they did an amazing job at talking me through and explaining each treatment. I am over the moon with the results and would highly recommend Esvita.


Useful

Share

Advertisement
Chris Heath
GB
•
3 reviews
Sep 23, 2025
Rated 5 out of 5 stars
Great experience for my hair treatment from the very start…
From the very start my consultation with Liam grant went smoothly and he was totally on the ball with all my questions and answers ! It was a very quick process booked the week before I went due to my availability and theirs which lined up great for everyone the price quoted was the price paid no hidden extras and no pushy selling when you got there ! They even helped find me a flight which was under £100 return ! Picked me up from the airport straight to 5 star hotel then transferred in the morning ! They had a videographer her name was "Hacer"spoke English and very keen to do a great job of photoing my day !! Skyler was my interpreter from the start of my treatment to the end and kept me informed of everything that was being said very well done no issues ! The treatment went smoothly it took about 8 hours for the whole process top crown and front of hair 4000 grafts ! I must admit I fell asleep a few times just because I felt so at ease with the whole process there !!overall experience with everyone I met was fantastic could not fault Esvita at all !my treatment came with a guarantee and since home I've had no issues and just sending photos and texts to Liam so the procedure is monitored for healing etc any questions I have or had were answered fully and to my great satisfaction !!well done again to all at Esvita clinic !! Will definitely be using them for further


Useful

Share

customer
AU
•
3 reviews
Sep 18, 2025
Rated 1 out of 5 stars
My second bad experience with esvita…
My second bad experience with esvita clinic.

I went for do 3 implant and veneers in June.

Here under 3 month after I have lose 2 veneers.

Went with them again 2 weeks after for sugery after I do my teeth some also end up in a expensive nightmare

When everything should be healed up and be good all the problems first starting to come and they don't take any responsibility for it

People need be really careful, they provide good service until something happend and there are no more service..

Be really carefull with esvita clinic



Useful
2

Share

Shay Skivington
US
•
1 review
Sep 17, 2025
Rated 5 out of 5 stars
My experience was made very enjoyable…
My experience was made very enjoyable with the help with All the team from evista clinic


Useful

Share

Colum O'Brien
IE
•
1 review
Sep 14, 2025
Rated 5 out of 5 stars
Fantastic experience thank you.
Fantastic experience thank you.


Useful

Share

Advertisement
Ross
GB
•
4 reviews
Sep 13, 2025
Rated 5 out of 5 stars
Very helpful and amazing service I…
Very helpful and amazing service I absolutely love my teeth I'd recommend Esvita clinic 100%


Useful

Share

Robert Redmond
IE
•
5 reviews
Updated Sep 7, 2025
Rated 5 out of 5 stars
I was seeking reputable clinic in…
I was seeking a reputable clinic in Turkey for hair transplant. I made contact with several but one caught my attention because of the reply I received. Nadine sent me details of Esvita Clinic in Istanbul. Communicating with her I found her to be straight, polite & respectful. I ended up booking a visit to Esvita. The medics there were extremely professional, helpful, and curtious. I was delighted with the treatment and the result. I highly recommend Esvita clinic.


Useful

Share

Tomas Rudokas
TR
•
1 review
Sep 5, 2025
Rated 5 out of 5 stars
l am happy for trasplat her l will beg…
l am happy for trasplat her l will beg again for second time.


Useful

Share

Jane Sauzande
GB
•
12 reviews
Sep 2, 2025
Rated 5 out of 5 stars
Esvita Clinic

Esvita Clinic
Come from the UK to Turkey,
Esvita Clinic to get my new teeth very good clinic



Useful

Share

Advertisement

BM VIDEO
PL
•
1 review
Sep 2, 2025
Rated 5 out of 5 stars
Very good service!!
Very good service!!! Highly recommended!!!


Useful

Share

See if a website is trustworthy without leaving the page


Steven Scirkovich
NZ
•
1 review
Aug 25, 2025
Rated 5 out of 5 stars
Communication from the start was very…
Communication from the start was very good, very transparent. The treatment was as described. I travelled a long way, they went out of their way to make me feel comfortable, as well as my support friend who didn't come for treatment. Very satisfied.


Useful

Share

Veronica Micic
DE
•
5 reviews
Aug 20, 2025
Rated 5 out of 5 stars
Crowns veneers
This was my second time with Esvita for dental work. Two years ago, I had 8 crowns placed on my upper jaw. The teeth were done well, but since I didn't do the lower jaw at the time, my bite wasn't properly adjusted. The dentist had advised me to complete everything together, but I wasn't convinced then.

After two years, my bite became too uncomfortable, so I returned. I originally planned to treat only the lower jaw but ended up replacing all of my upper and lower teeth, including the previously done crowns. This time, I knew exactly what I wanted and had done thorough research.

Although my previous crowns were nice, they didn't really suit my face. This time, I wanted a more natural look, so I showed the dentist a photo of my desired result. My dentist was Huseyin (or Hilmi) from Livera Clinic. He speaks English, which made communication so much easier. He explained everything clearly—what he would do, how, and why. He was amazing, gentle, and most importantly, he did an excellent job. My new teeth look natural, they match the photo I showed him, and they truly suit my face.

Lesson learned: Go into this process informed. Review the dentist's work beforehand and make sure it matches the look you want. Also, keep in mind that this is not Australia or America—there are cultural differences in communication and scheduling. For example, I am used to having all appointment details confirmed well in advance, but in Turkey, things are more flexible. Appointments are usually scheduled the evening before for the next day, so adjust your expectations accordingly.


Useful

Share


Gatis Vuškāns
TR
•
1 review
Aug 19, 2025
Rated 5 out of 5 stars

Verified
Great clinic and staff
I had 28 crowns done, and the whole experience was absolutely fantastic! The staff is incredibly friendly, welcoming, and professional, making me feel completely at ease throughout the entire process. The results are even better than I ever imagined.
The clinic and hotel are spotless, and having the hotel stay included in the package made everything so easy and comfortable. I'm thrilled with my new smile — if you're considering dental work, this clinic is truly the real deal!
I'd especially like to personally thank my coordinator, Valeria, for her warm and heartfelt care during the entire process. Alex deserves a big shoutout as well for helping me with even the more unusual requests — like arranging a second monitor for my work! And of course, a huge thank you to my specialist, Husseyin, for helping me achieve the smile of my dreams.


Useful
1

Share

Advertisement

Ken Davies
GB
•
52 reviews
Aug 9, 2025
Rated 1 out of 5 stars
Poor company
Due to get treatment on the 30th of August 2025 . Sent them a message 3 weeks before im due to arrive. Good job I did as they have now informed me they can't carry out the treatment.
Stay clear of this clinic as they are not what they seem.


Useful
1

Share


Jay Cole
GB
•
1 review
Aug 6, 2025
Rated 5 out of 5 stars
Great clinic
Great clinic, great service. Nelly was excellent & very helpful start to finish!

Can't thank them enough, love my new smile.

Five stars all the way !


Useful

Share

Marcin Wiśniewski
GB
•
4 reviews
Jul 31, 2025
Rated 5 out of 5 stars
Very professional and staff very nice

Useful

Share


jaryd erricker
TR
•
1 review
Jul 26, 2025
Rated 5 out of 5 stars
I reached out to esvita after finding…
I reached out to esvita after finding this amazing clinic through Instagram. firstly I'd like to give a massive shout out to Lisa my medical advising for her prompt response and help with any questions I had her service was second to none. Also would like to thank my dentist Hussain for his amazing work I couldn't be happier with how natural and strait my teeth turned out all the staff esvita have been more amazing and would recommend to anyone thinking about a procedure to jump right in ✨🙌🏽


Useful

Share

Advertisement
Mr Jon H
GB
•
5 reviews
Jul 17, 2025
Rated 5 out of 5 stars
I had my teeth done by the team in…
I had my teeth done by the team in Istanbul back in April, and I've had absolutely no issues since.

My dentist here in the UK commented that the work was done to a high standard, and both my gums and X-rays show no signs of any problems at all.

Thank you again for giving me my smile back — I couldn't be happier! 😊


Useful

Share


Mark McBreeze
GB
•
2 reviews
Jul 13, 2025
Rated 5 out of 5 stars
Parisa is the best for this firm .She…
Parisa is the best for this firm .She made my life a lot easier and we love her like family.Parisa is the aspect of this business and she is amazing.


Useful

Share


mark mc breeze
GB
•
16 reviews
Jul 9, 2025
Rated 5 out of 5 stars
I had my up and downs with this…
I had my up and downs with this firm.But there amazing people and Parisa Is lovely. I will give them another go and see if I can get what I ask for.




Niall wright
GB
•
9 reviews
Jun 30, 2025
Rated 5 out of 5 stars
An amazing experience from start to…
An amazing experience from start to finish I'm so so happy with my new teeth there even better than I expected. . Do t worry about the sensitivity it wears off. Just enjoy your brand new smile like I'm doing now.


Useful

Share

Advertisement
Alfredas
GB
•
6 reviews
Jun 28, 2025
Rated 5 out of 5 stars
Its been nice company nice people…
Its been nice company nice people ewriting explained doctors its best what i have see ,I love my teeth


Useful

Share

customer
GB
•
4 reviews
Jun 28, 2025
Rated 5 out of 5 stars
My experience with this clinic has been…
My experience with this clinic has been amazing , couldn't fault them at all, I would totally recommend this dentist to everyone , they are so nice here , they take care of you even if you are nervous , they are very gentle , the best clinic I have ever used , changed my whole life !!!


Useful

Share

Daniel Derren Butler
GB
•
2 reviews
Jun 27, 2025
Rated 5 out of 5 stars
everything from start to finish was…
everything from start to finish was brilliant
the dentist was out of this world changed my whole life , clean and friendly dentist i couldn't recommend a better place . everyone in the dentist makes u feel at home very good experiance from start to finish not a single issue i'm over the moon 👌


Useful

Share

joe hislop
NL
•
6 reviews
Jun 17, 2025
Rated 5 out of 5 stars
Absolutely thrilled with my results! A huge thank you to Esvita for transforming my smile with care, skill, and precision. #PatientReview #SmileMakeover
I can't thank the amazing team at Esvita enough for the incredible care and results. From day one, Alex made me feel completely at ease and walked me through every step with patience and professionalism. Nelly and Valerie were absolute stars—so friendly, attentive, and skilled throughout the process. And Edward, thank you for your precision and artistry—you've truly transformed my smile!

I've never felt more confident. If you're thinking of upgrading your smile, I highly recommend this team. Five stars all the way! ⭐️⭐️⭐️⭐️⭐️


Useful

Share

Advertisement

Cleyton Rosa
GB
•
2 reviews
Jun 4, 2025
Rated 5 out of 5 stars
Great experience at clinic the team are…
Great experience at clinic the team are very professional and they redone my full smile makeover in 1 week thank you esvita .


Useful

Share

Simon Smith
GB
•
2 reviews
May 31, 2025
Rated 5 out of 5 stars
I decided to choose Esvita Clinic for…
I decided to choose Esvita Clinic for my dental work and it was definitely the right decision. From start to finish these guys have been amazing. At certain points during the process you might think what the hell have i done, but trust the process these guys know exactly what they are doing and I couldn't be happier with the end results. After 22 years of hating my teeth I can finally smile again 😁


Useful

Share

Chloe Mc Laughlin
GB
•
6 reviews
May 26, 2025
Rated 1 out of 5 stars
Avoid Avoid & Avoid Again!!!!!
Avoid Avoid & Avoid Again!!!!!! After many attempts, we have not been able to find a solution. Provincial Directorate of Health has been in contact with us again and we have lodged an official complaint. Also contacted the relevant avenues in UK to be sure people from UK & Ireland know to avoid this clinic at all costs. Misleadingly, you will have the upselling and unnecessary costs following a trip here.


Useful
4

Share

Donna
AU
•
1 review
May 21, 2025
Rated 5 out of 5 stars
Smile make over
I came to Esvita clinic for a smile makeover.
Staff at esvita were amazing and the dentists were so dedicated to creating a perfect smile.
The clinic is clean and modern.
If you are looking to get a hollywood smile or smile make over. Please consider Esvita clinic.
I can highly recommend esvita clinic.


Useful

Share

Advertisement

Vsevolod Ganiushkin
PT
•
2 reviews
May 21, 2025
Rated 5 out of 5 stars
Hair transplant review
I had a hair transplant procedure. The doctors and consultants were very reliable. Doctor offered me additional procedure to increase chance to keep new hairs. It was quite pricey but I agreed to do that. Hair transplant procedure was mostly painless.
Transportation service and hotel are good as well.
If I decided to do some plastic surgery I'll choose Esvita Clinic next time.


Useful

Share

See if a website is trustworthy without leaving the page



Davide V.
GB
•
9 reviews
May 20, 2025
Rated 5 out of 5 stars
Organisation was a TOP Level
Esvita did absolutely great service from beginning to end, Hotel , communication, doctors everything was a top level , I did hair transplant and my tooth too . Eva my supervisor was absolutely brilliant 🤩 All team was great . Thanks
Davide


Useful

Share

customer
GB
•
2 reviews
May 17, 2025
Rated 5 out of 5 stars
I came to esvita to fix my teeth and…
I came to esvita to fix my teeth and had 25 crowns everything went smoothly and all nice people I would recommend to anyone


Useful

Share


Ali Soumaré
GB
•
1 review
May 17, 2025
Rated 5 out of 5 stars

Verified
I had the best experience .
I had the best experience .
The clinic was super clean state of art équipements.
They were so fast and efficient.
Couldn't be happier and they level of customers services is absolutely top top !


Useful

Share

Advertisement
Kènza Charkaoui
GB
•
3 reviews
May 15, 2025
Rated 5 out of 5 stars
Great experience
Great experience, outstanding dentist; the equipment is all out of this world all up to date , I've never seen these types of equipment.
Also the hygiene is taken very!
Overall Esvita clinic gets a 10/10 from
Thanks for everything


Useful

Share


Charlie Davey
AU
•
3 reviews
Updated Oct 31, 2025
Rated 5 out of 5 stars
Fantastic
All very professional so far, will update in 4 months when I can see the full results

Update, been nearly 6 months now and results are amazing, I'm so happy!!!


Useful

Share


Mohamed Jama
GB
•
5 reviews
May 5, 2025
Rated 5 out of 5 stars
I came to esvita clinick to do my…
I came to esvita clinick to do my teeth done the service I had was fantastic, the staff here is very welcoming.
I hated smiling at people because my teeth was all over the place but now I can smile with confident.
Thank you again for all the Esvita clinics team.

Want to have a happy smile go no further 😊 Esvita Esvita clinick.

Mohamed jama
From UK 🇬🇧.


Useful

Share

Aaron Montgomery
GB
•
3 reviews
May 5, 2025
Rated 5 out of 5 stars
I came from Sunderland ,UK to esvita…
I came from Sunderland ,UK to esvita clinic and they are absolutely incredible from start to finish the staff who work here go above and beyond beyond to help you
The co-ordinators are very friendly and helpful to always remind ding you of appointments etc there was a lot of people from my age group and various other ages this is how I knew they were the best in istanbul ⭐️⭐️⭐️⭐️⭐️


Useful

Share

Advertisement

Adam Stephenson
GB
•
9 reviews
Apr 29, 2025
Rated 5 out of 5 stars
Excellent team and 5 * service from start to finish!! Highly recommended
Cannot fault these guys, excellent service!! I came for my teeth and wish I'd have done it sooner! For decades I've struggled with my teeth and confidence because of them, now after just 3 days here I can smile with my teeth showing and slowly getting my confidence back. Looking forward to the final step! Really caring team, modern clinic with all the latest tech. Lifts from the airport, to hotel to clinic each time and had a really good stay at the G Hotel. Highly recommend!


Useful

Share

Josh
GB
•
1 review
Updated Apr 5, 2025
Rated 1 out of 5 stars
MY TEETH HAVE FALLEN OUT !, do not risk your health with this clinic
Esvita to my told me I was having 24 teeth , and then only gave me 21 teeth but didn't try tell me or say anything til I noticed when I arrived home. they put my teeth in 4 hours before my flight home and didn't check to see if they was fine.
3 weeks later I have a wobbly implant and a week after that my whole implant has come out everything has been a problem from the start and they have serious attitude problems and are simply out to get as much money as possible from you , please be care full I wouldn't wish my experience on anyone , and when I have told them I'm going to write this review they said they are aware of fake reviews , I would post pictures if I could … stay away from here


Useful
2

Share


Daniel Danielewicz
PL
•
1 review
Mar 21, 2025
Rated 5 out of 5 stars
I am so happy that I have found this…
I am so happy that I have found this clinic. I have been here twice. First time in November to do the implants and second time this week to finish my new smile. I am so satisfied with all the treatments. Everything here was 5 star experience. I highly recommend this place.


Shaun Findlay
AU
•
3 reviews
Mar 14, 2025
Rated 5 out of 5 stars
Excellent work
Excellent work. From first contact to finished product Esvita Clinic have gone above and beyond to provide an exceptional service. Highly recommend


Useful

Share

Advertisement
Vladas
UA
•
2 reviews
Mar 13, 2025
Rated 5 out of 5 stars
I came to Esvita clinic for teeth
I came to Esvita clinic for teeth, I didn't have any teeth on my upper jaw. The work was amazing they do for me titanium hybrid and crowns and looks really perfect. I want to say big thanks especially for planning team, my translator Marina, my consultant Nikolay, and drover Levent. THANKS FOR EVERYTHING ESVITA


Useful

Share

Ayyah Erekat
GB
•
2 reviews
Feb 17, 2025
Rated 5 out of 5 stars
Excellent service made me feel really…
Excellent service made me feel really comfortable the team is amazing and very welcoming and friendly and their job is amazing. I love my new smile 😊

Thank you esvita clinic ❤️😊


Useful

Share

Chan
GB
•
1 review
Feb 16, 2025
Rated 1 out of 5 stars
Do not use this clinic
Do not use this clinic, the coordinator are unprofessional. The dentist are to busy they shaved my teeth then left to the last day to put in my crowns, been in consent pain since using painkillers for nearly 3 months now and when you reach back out to them they have attitude. Do not go through Alex the coordinator he has no respect for women he was shouting at me being bery rude & dismissive to my problem. the dentist men are racist, they don't like women asking any questions. They don't want other patients to here your issues in the clinic to lose custom so any concerns or issues you have after your crowns have been fitted gets all brushed underbthe carpet. I've been left with server pain ever since I used them, they told me 20 years warranty before they done job. Now they messed up they've change it to 1 year. Poor customer service rate this clinic a 0, I have to pay for further treatment in london to true and get to the bottom of this pain. After esvita done my scans and saw no infections in my mouth before and after treatment but they still want to give me 6 route canal what for, they take your money, lie on the services needed and the after care is diabolical. USE AT YOUR OWN RISK SERVICE IS TERRIBLE.


Useful
2

Share

Josh Heath
GB
•
1 review
Updated Feb 13, 2025
Rated 1 out of 5 stars
Esvita are unorganised and will leave you will last minute
The worst !! I was there 7 days they put the prices up on arrival got my teeth shaved down the second day and didn't get my teeth put in until 3 hours before I was leaving , the salesmen are just trying to get your money


Useful
2

Share

Advertisement
Carl rogers
GB
•
1 review
Feb 8, 2025
Rated 3 out of 5 stars
Medication
Overall treatment was good however I was medication with no instructions as to when to take the pills , I only received information the following day and I should of taken the medication to prevent swelling, this is not professional and lack of communication is bad


Useful

Share

Dmitry Prygunov
AU
•
2 reviews
Feb 4, 2025
Rated 5 out of 5 stars
Was a great experience!very happy with…
Was a great experience!very happy with translator Marina!Was very organised and easy transplantation!Highly recommend.thanks


Useful

Share

Alex P
GB
•
3 reviews
Feb 3, 2025
Rated 5 out of 5 stars
Thanks Esvita
The people's everybody was very helpful and very friendly. They made the process easier. Alex and Marina answered to all my questions and guided me through. I am looking forward to see also the results. Thank you for everything! 🙏


Useful

Share

Andrew
GB
•
2 reviews
Jan 31, 2025
Rated 5 out of 5 stars
Overall experience was great from start…
Overall experience was great from start to finish the pick up from hotel to clinic was on time every time .Amelia was great assistance and very polite and welcoming all round very good clinic very clean would highly recommend


Useful
1

Share

Advertisement
Kyle walker
GB
•
2 reviews
Jan 31, 2025
Rated 5 out of 5 stars
Very happy with esvita clinic and there…
Very happy with esvita clinic and there staff, there great transfers and translators make the experience very relaxing and easy to manage
And a massive thank you to Alex and Amelia for taking great care of me during my time here


Useful

Share

See if a website is trustworthy without leaving the page



Fabs
MT
•
5 reviews
Jan 30, 2025
Rated 5 out of 5 stars
Professional
Professional, friendly staff.
High tech facilities.
100% recommended.


Useful

Share

uldis Stankēvičs
DK
•
1 review
Jan 26, 2025
Rated 5 out of 5 stars

Verified
First visit (2025 January)
When you start your research about clinics in Turkey,its so much info with reviews that its hard to understand what is right and what is not. We chose Esvita clinic because of good reviews from our friends,who have been there

So we went to Istambul in 19 of January and already people was waiting for us (They made a small video how to find meeting point,because airport is huge-that was nice touch )
We went to hotel and next day I had apointment for consultation with the doctor and made the final plan and day after we started the treatment
I will not lie,I was scared ,but all the staff is great and supportive and the doctors are amazing 👍 I was suprised that it didnt hurt, first day they put 4 implants in and after that you can go and enjoy Istambul 👍
On Thursday we were finished with everything and we are very happy that we chose Esvita

Small niances can always happen,but guys in clinic did their best to avoid it

Thanks to All Esvita staff and Drivers
And special thanks to Alex- You were big support and thank you for the effort you put in your Job 🥳👍


Useful

Share

Kaja Gajdziszewska
PL
•
1 review
Jan 7, 2025
Rated 5 out of 5 stars
Contented customers
He are so happy about the services of ESVITA Clinic. My boyfriend had a nose job and a hair transplant - both procedures went very smooth and well. Our translators Amelia and Valeria were such helpful people. They were smiling a lot and they did their best to make us feel comfortable and taken care of. Even greater thanks to Robert, our representative, who was always there to support us and explain everything. He was online all day long, even until late evening hours, so we felt contented. We are definitely going to recommend services of ESVITA Clinic to all our friends.


Useful

Share

Advertisement
Hamza A
GB
•
4 reviews
Dec 31, 2024
Rated 5 out of 5 stars
Smile makeover
Getting my new teeth has been such a game changer, I'm so happy with them! Everything went so smoothly, better than I could have imagined. It's such a relief to have it all done, and I can't stop smiling. A big shout out to William who organized this all – they made everything so easy. Clear communication throughout the whole process was key, and I really appreciated it. And A big thank you to Ervin and team. Would definitely recommend family and friends to come here!


Useful

Share

Michael
AU
•
2 reviews
Dec 19, 2024
Rated 5 out of 5 stars
The uplifting natural ambience of joy…
The uplifting natural ambience of joy gave me a homely feeling!
I felt so attached the moment I arrived having Serena as my interpreter and Robert as my medical advisor, even the drivers very welcoming, gave me so much comfort, and I'll be sad to leave.
No exceptions it's the best dental group I've ever experienced and I will be returning soon.
THANK YOU ESVITA CLINIC !


Useful

Share


Julia Giles
GB
•
11 reviews
Dec 11, 2024
Rated 5 out of 5 stars
I am baffled at the 1 star reviews on…
I am baffled at the 1 star reviews on here! Firstly I never paid a deposit, I just had to show them my flight ticket. Secondly the team are amazing! Safa, Serena, Dr Irvin and the drivers were totally professional, on time and super friendly 👏 I have suffered no pain and the whole procedure for 20 crowns was over in 3 days! Yes, everything is agreed on WhatsApp and its a very efficient and economical way of doing things, thus, keeping costs down. I would use them again in a heartbeat 💓 ♥️ ❤️ thank you so much xxx


Useful

Share

Naomi
GB
•
6 reviews
Nov 29, 2024
Rated 5 out of 5 stars
From the first message esvita have been…
From the first message esvita have been so helpful and understanding, the communication between myself and staff has been amazing. I was really nervous but Alex, Safa and Serena made me feel so comfortable and at home. They talked me threw everything they was going to do and did it all at a pace that was comfortable for me. I'd 100% recommend I've had the best experience and wouldn't have changed a thing. Thank you all so much for everything you've done for me and for giving me back my confidence


Useful

Share

Advertisement
kelsey johnson
GB
•
3 reviews
Nov 22, 2024
Rated 5 out of 5 stars
I was very skeptical coming to Turkey…
I was very skeptical coming to Turkey from London for my teeth but it was the best decision I ever made! I am beyond happy. The communication was great especially with help from Safa and Alex, my dentist Irvin was brilliant and really put my needs first.
Would recommend to anyone


Useful

Share

Damon Phelps
GB
•
1 review
Nov 17, 2024
Rated 5 out of 5 stars

Verified
A Confidence Boost in Every Way
 I had been considering a smile makeover for a long time, and Esvita Clinic was highly recommended. Safa was very welcoming, and Alex, my medical advisor, gave me all the details I needed to feel comfortable. The makeover itself is subtle yet effective—I feel like a new person without feeling like I've changed drastically. My teeth look better, but they still feel like mine. This was exactly what I wanted, and I'm so grateful for the support from the Esvita team.


Useful

Share

Paulina
GB
•
4 reviews
Sep 24, 2024
Rated 1 out of 5 stars
Avoid this clinic
Avoid this clinic, after doing so much research on the clinic and seeing the good reviews I avoided any bad reviews. They drew up my plan and gave me my quote. I paid £1.5k deposit and when I came to the clinic they told me they had to do a whole nother plan that cost more. My innitial plan was suppose to cost me £4k and when I refused they promised me another treatment. I told them I do not want to file my teeth and when I was going to do the procedure they numbed my mouth and filed all my teeth and told me I NEED TO DO ANOTHER PLAN "Because it will Make my teeth more better and give me a nicer smile " they then put my plan up to 6k and told me I need to do that plan. I have had to book an emergency appointment in the uk with a dentist as there has been inflammation around my gums and I have had to be put on antibiotics due to an infection. My teeth have gone from being bad to even worse and they have shaven them down to half the size of my original tooth. They was pushing me to get another treatment when I told them I didn't want it. Now I have to suffer with pain and have to book cosmetic treatment as people refuse to "work with Turkey teeth" in the uk




Dennis ryan
GB
•
6 reviews
Sep 22, 2024
Rated 1 out of 5 stars
poor customer services
Well.

what can I say.

I nearly made the mistake if using estvita.
but there seemed to be red flags,

but the sole reason , for me choosing a different place , was the extremely unprofessional Robert Wood,

if it was not for his u professional approach, and also trying to slander other companies, to gain a sale ,

this may of got successfully.

even after telling him, I have decided to go else where, his approach, was extremely poor.

so unfortunately esvita , as a company you may have some good results or not.

but your sales man ROBERT WOOD , HAS created this review,

for consistency really poor customer service and unprofessional approach,


Useful
2

Share

Advertisement
Iveta
TR
•
1 review
Sep 19, 2024
Rated 5 out of 5 stars
After a very bad and unpleasant…
After a very bad and unpleasant experience at another clinic ,you promptly took care of me,and during my first personal meeting with you.I calmed down again and trusted in something for which I traveled to Istanbul.Thank you for your complete professionalism regarding health care and I'm looking forward to everything being done in a few months and I'll be smiling beautifully ať my husband for the next few months 🙂😉


Useful

Share


Ger Vė
TR
•
1 review
Aug 21, 2024
Rated 5 out of 5 stars
Thanks
Anna good translator, and friendly girl.
All others good guys and girls, all friendly, can help you if you want some.
Thanks for all 😘


Useful

Share


Sokol Dedaj
US
•
1 review
Jul 27, 2024
Rated 1 out of 5 stars
Doctor is an amatour
I talked to them with camera and he told me l will have a full coverage with 7000 grafts if l pay extra 200 dollar to use my beard like a donor area too,flied from Detroit to Istambul and the first thing the doctor asked me in the morning "How do you want to pay" even l gave them 200$ downpayment,he started doing my hairline without using a red lazer or measure or anything because they dont have it pretending l dont need them because l am "artist" for this and l asked him just dont go low than my natural line and cover my sides and he did a line 1 cm or more lower than my natural hair and in the sides went so high,l told him l dont like this he said thats how l know to do and when he saw my reaction told me ok l will cover the sides and l will go upper in the middle,they shaved my head and they didnt wash it before hair transplant,the clinic wasnt in good clean condition,durint the surgery he didnt want to use my beard for donor area as we talked even l alredy had paid him but after l insisted he told one nurse to take like 100 grafts from my beard just to look like he did his job,after 2 times surgery my hairline was 1 cm lower and straight as hell,l told him what is that he told me looks like this now but after 4 months will look better,he gave me some products to use after 3 months and l paid another 200$ and when l asked him after 3 months he told me dont use them,now l
Have a lot of bold areas in my head and hairline is ashame,l told him what has he been thinking doing this,we cant help you because he demaged your donor area completely,l write a lot of comments in their instagram page but they deleted them like they do with anybody who complain,they dont text me back anymore,the best person there was the translator but if you really dont want to regreat for all the rest of your life dont choose this clinic for a hair transplant,if anybody think l am lying l can show my results and if the doctor has any video of mine doing hairline with laser or any bla bla like they do he can post it in their page but they dont have elementary things for that,he is good in theory in the stories but in practice is a failure.And l think all these good review are with fake accounts are from clinic employers just to look like they are the one.


Useful
1

Share


Juan Garza
MX
•
2 reviews
Jul 22, 2024
Rated 5 out of 5 stars
The hair transplant experience was…
The hair transplant experience was great over this past weekend. From the drivers to the amazing translator Anna who was really nice all the time and still the constant support of Robert. The clinic where everything happen was nice, the nurses and the doctor who also performed the transplant with the dhi pen. I will need to wait for results for sure but everything was according to plan and now it is also part of my job to ensure i take good care of my head.

I definitely recommend this experience with this clinic.


Useful

Share

Advertisement

Nasser
TR
•
1 review
Jun 13, 2024
Rated 5 out of 5 stars
My first interaction with Estiva Clinic…
My first interaction with Estiva Clinic was about month ago. When I was looking among bunch of clinics to do dental and hair treatment. After I discussed details with each one of them Estiva was my final choice. And thank God I did.
I dealt with Cindy from the Planing, Safa from dental office and Valery the translator from hair transplant.
They were all professional and friendly. But my main interaction was with Cindy. She helped me with the visa process, transportation from the airport and the hotel to the clinic. She did exactly what she promised me the first time. I'm very happy with the results and the experience overall. As for my dantal experience Dr Kubra was my dentist. She very professional passionate about her job. She takes care of small details to make sure everything is perfect. Thank you Dr. Kubra .
As business owner myself, I believe in the importance of the company customer service. Therefore I congratulate Estiva Clinic of their investment of people like Cindy, they're lucky to have an employee like her. Without her first interaction, I might be ended up with other clinic. And I thank God I didn't.
Thank You Cindy 🙏🏻
I'm sharing with you detail photos throughout my treatment.


Useful

Share



marnix herreman
ES
•
1 review
May 22, 2024
Rated 5 out of 5 stars
Marnix Herreman 72 jaar …
Ik ben Marnix Herreman 72 jaar en na lang aarzelen ben ik dan toch afgereisd naar ESVITA CLINIC te Istanboel om mijn lelijke mond met afgebrokkelde tanden te laten behandelen ! Ontvangst, organisatie, werknemers, dokters en behandelingen waren dik in orde, niet tegenstaande dat men mij een Clinique afraadde en een privé dokter aanraadde ! Het is mooi comfortabel en zie veel jonger uit ! In België en Spanje is iedereen heel enthousiast over het resultaat van mijn behandeling dus; Esvita is een aanrader als je als je van plan bent met een Hollywood smile wil gezien worden ! Marnix .

Marnix Herreman 72 years old…
I am Marnix Herreman, 72 years old and after much hesitation I traveled to ESVITA CLINIC in Istanbul to have my ugly mouth with chipped teeth treated! Reception, organization, employees, doctors and treatments were excellent, despite the fact that they advised me against a Clinique and recommended a private doctor! It is nice and comfortable and looks much younger! In Belgium and Spain everyone is very enthusiastic about the result of my treatment; Esvita is highly recommended if you want to be seen with a Hollywood smile! Marnix .
Date of experience: May 22, 2024


Useful

Share

AM
GB
•
2 reviews
May 21, 2024
Rated 5 out of 5 stars
Heartfelt Thanks for a Wonderful Hair…
Heartfelt Thanks for a Wonderful Hair Transplant Experience in Istanbul

We wanted to extend my deepest gratitude for the outstanding care and service I received during our recent hair transplant procedure at your clinic in Istanbul at Esvita clinic.

From the initial consultation to the post-operative care, every aspect of my experience was exceptional. The professionalism and expertise of your team made is feel comfortable and confident throughout the process. I am thrilled with the results and can already see a positive change. Speaking to Robert Wood from the whatsapp consultation was amazing to meeting the whole team and the Doctor Yigit Hamdemir whom was amazing doing the procedure and the English translator was very nice too.

Visiting Istanbul was also a delightful experience. The city's rich culture, history, and hospitality added to the overall positive journey. I appreciate the warm welcome and the seamless coordination that made my stay pleasant and stress-free. The hotel was amazing top service and the airport transport together with the clinic transfers from the hotel to the clinic.

Thank you once again for everything. we will highly recommend their services to anyone considering a hair transplant.


Useful

Share

James bailey
TR
•
1 review
Apr 22, 2024
Rated 5 out of 5 stars
Couldn't of wished for an easier…
Couldn't of wished for an easier experience the fact I have a fear of dentist. To have a full rip out and to be made at ease was lovely. Lamyaa has made this very easy for me to suck a lovely translator. And a big shout out to the manager hussein lovely man. Looking forward to coming back in 6 months to be finished off with my Hollywood smile


Useful

Share

Advertisement
Nilofer Patel
GB
•
7 reviews
Apr 22, 2024
Rated 5 out of 5 stars
the experience was great and the…
the experience was great and the consultant Sara and aafiya was great with every bit of explanation and clearing all doubts and questions coming to mind hospital staff was good too.all of my flying to the hospital to the hotel or to any consultation with doctor every bit of it was well planned and well organised..definitely giving 10* star overall really happy for the result what I have came for and worth my trip all the uk to turkey..


Useful

Share

See if a website is trustworthy without leaving the page


Laura Svetlova
NL
•
1 review
Mar 30, 2024
Rated 5 out of 5 stars
Thank you Esvita & Parisa!!
I actually was so shocked about how the process in Esvita Clinic is fast and well organised! I didn't need to think about anything, felt like a princess - car transfer, water, coffee, medications. I was so welcomed and I can say huge thanks to my coordinator Parisa who is one of the reasons why I chose exactly Esvita Clinic. Thank you very much, my result is amazing!


Useful

Share

Ahmet Djafer
GB
•
9 reviews
Mar 29, 2024
Rated 5 out of 5 stars
My journey
My exprance would the hospital was first class all the staff and support staff were so helpful,i was made to feel so welcome and the lady ms Afiaa a great asset to the company.


Useful

Share


Suzan Minassian
SE
•
2 reviews
Mar 28, 2024
Rated 5 out of 5 stars
I came from Sweden to Turkey for my…
I came from Sweden to Turkey for my surgery. I choose Esvita because they were very helpful from the beginning to the end. I'm thrilled with the results I've gotten. I did liposuction, breast lift and foxy eyes and the results are amazing!

I highly recommend Esvita if anyone wants to do any procedure!

A big thank you to Parisa and Afiaa for their support and services! They made my dream come true!


Useful

Share

Advertisement
Mandy
NL
•
8 reviews
Mar 18, 2024
Rated 5 out of 5 stars
Everything was organized very well
Everything was organized very well. From the pickup from the airport to the hotel , all the drivers every day. The communication with Milya and Henry Davis. Henry has helped me since the beginning. The hotel was absolutely amazing. The shaving of my teeth was a scary experience for me, but thanks to the dentist and her assistant I experienced it as pleasant. They were very careful. Understanding and helped me face my fears. They made sure I felt safe. They listened carefully what my wishes were
And made sure I didn't have to worry about
The results. And they were right. The results are amazing. Beyond my wildest dreams. I am so happy I chose esvita. I would definitely recommend them if you want a new
Smile. In the future I will contact them if there are more procedures I would like to have.

Thank you esvita!!!!


Useful

Share


Valdimar Th.
IS
•
2 reviews
Updated Mar 14, 2024
Rated 5 out of 5 stars
I can truly recommend the Clinic
I can truly recommend the Clinic. Professional staff and friendly. I'm very happy with the results. Afiaa the translator was very helpful and always there for me.
My coach Robert was always there for me to, his knowledge and care was very important.


Useful

Share

mark phillipson
GB
•
3 reviews
Mar 4, 2024
Rated 1 out of 5 stars
Still no refund for my flight money…
Still no refund for my flight money even though Pegasus airlines say it's in your Bank account so why is that money not been refunded to me


Useful
1

Share

Gavin Gent
GB
•
5 reviews
Feb 27, 2024
Rated 5 out of 5 stars
This is my first visit
This is my first visit , whereas I need to come back after three months to be finalised , this first visit has been an amazing experience, I've been looked after like royalty, I've been picked up and taken from and to everywhere I needed to be , the consultants are on the end of WhatsApp day and night and answer any questions you have almost immediately 🙏 so pleased with the treatment so far , can't wait to come back and see the final results 🙏


Useful

Share

Advertisement
Sultan N
GB
•
2 reviews
Feb 19, 2024
Rated 5 out of 5 stars
Esvita handled everything very…
Esvita handled everything very professionally and the care provided during and after treatment was fantastic. Thomas was my main contact throughout the process and was always at hand with any questions and queries. He and Aafia dealt with my appointments and I was very happy and satisfied with the service and care. Dr Kubra was a true professional and I trusted her to provide me with the best results and she did exactly that. I'm so happy with my results and I want to thank everyone who was part of my journey!


Useful

Share

Patrick Gilroy
US
•
4 reviews
Dec 2, 2023
Rated 5 out of 5 stars
Esvita is made up of an amazing group…
Esvita is made up of an amazing group of people that truly care about their patients. From the CEO to the drivers, from the surgeons to my translator, everyone went out of their way to make sure this American felt at home in Istanbul. I am excited to be headed home and soon my hair transplant will speak for itself…..Until then however I am that much richer having made my new friends from Esvita.


Useful

Share

Roger Everaer
BE
•
2 reviews
Nov 20, 2023
Rated 5 out of 5 stars
We came from Belgium
We came from Belgium. Me and my wife goe dental treatments and we are very happy to choose this clinic. Olivia and Valérie and all the were amazing. The doctor is doing very good job. And thank you The drivers.


Zaman alabadi Abadi
TR
•
1 review
Nov 18, 2023
Rated 5 out of 5 stars
Very nice clinic
Very nice clinic, they take good care of me and my family I am very happy with my results.


Useful

Share

Advertisement
Joakim
NO
•
9 reviews
Nov 15, 2023
Rated 5 out of 5 stars
Great service and arrangement

Useful

Share


Gundega Bērziņa
TR
•
1 review
Nov 6, 2023
Rated 5 out of 5 stars
Friendly and kind stuff
Friendly and kind stuff, great experience, beautiful result.


Useful

Share


Agris Berzins
TR
•
2 reviews
Nov 3, 2023
Rated 5 out of 5 stars
Everything is great planned and stuff…
Everything is great planned and stuff is amazing, thank you everyone!🇱🇻👍


Useful

Share


Cristina Razvan
RO
•
2 reviews
Aug 9, 2023
Rated 5 out of 5 stars
My husband make a hair transplant in…
My husband make a hair transplant in Esvita Clinic.after 6 months his hair is amaizing!!!people here was nicely,evrithing was perfect!


Useful

Share

Advertisement

Alaeddin Ayash
TR
•
1 review
Aug 1, 2023
Rated 5 out of 5 stars
Great job
Great job
totally recommended


Useful

Share


duke richard
IN
•
1 review
Aug 1, 2023
Rated 5 out of 5 stars
Definitely worth it 💯
I had an amazing experience here in esvita. Ryt from helping in visa process, to picking up from airport till dropping off from airport, and also providing 5 star hotel stay, they were very polite and professional..... The person incharge of me Alex tron , was also very brotherly, considering and polite... Amazing experience...highly recommend...

At first, i was shocked to see 3 people voted 1 star here in trust pilot, but later realised all 3 were the same person. I don't know what she went through, but I am quite surprised at her remarks. But I cannot comment on that as I never needed a refund, cause they were so good.


Useful
1

Share


Arbaz Ashraf
TR
•
1 review
Jul 31, 2023
Rated 5 out of 5 stars
They done my hair transplant very…
They done my hair transplant very professionally I write this review after 2 months to check the result. I was very shock to see my hairs growth. Really recommended this clinic.


Useful

Share


Syed Muhammed Yasir
TR
•
1 review
Jul 31, 2023
Rated 5 out of 5 stars
An unforgettable experience I had with…
An unforgettable experience I had with the dearest team of Esvita. I had my hair transplant treatment and implants installed in February. The team is amazing, picked me from airport escorted me to the hotel and the clinic team is so caring . I was nervous at first but after arriving they made me feel at home. I'm planning to come back in September to complete my smile with zircon crowns. I can't wait to see my smile transformation. My cousin will be coming too.

Highly recommend Estiva Clinic such caring and professional team.


Useful
1

Share

Advertisement

Mohammad Bani Hani
TR
•
1 review
Jul 31, 2023
Rated 5 out of 5 stars
Your best choice
A great company, service, and lovely crew


Useful
1

Share

See if a website is trustworthy without leaving the page



yasmine ka
TR
•
1 review
Jul 31, 2023
Rated 5 out of 5 stars
The best clinic and the best service…
The best clinic and the best service ever I'm very satisfied with the results I got everyone was very helpful the team the doctor I highly recommend


Useful
2

Share


Lucy Ferrer
US
•
1 review
May 27, 2023
Rated 1 out of 5 stars
promised a refund but blocked me after 2 months
they blocked me after 2 months of asking for my money. they asked me what my bank info was and then told me that it was incorrect. which goes to show that they were never going to refund me in the first place. ALL OF THE CORRESPONDING ACCOUNTS HAVE BLOCKED OR JUST DONT REPLY. i even asked for their legal teams email address and they don't even want to reply. i just want the money i should've been refunded in march. refer to the google review under Lucia Zurbitu for the full story. THESE PEOPLE ARE SCAMMERS AND THIEVES.


Useful

Share


Lucy Lopez
TR
•
1 review
May 11, 2023
Rated 1 out of 5 stars
refusing to refund me due to them stealing it
i've been asking for a refund for 2 months as i was not able to go due ti a family emergency. they have been avoiding me ever since and have threatened to sue me if i continue to ask for a refund. THIS IS A JOKE FOR A CLINIC. YOU'RE BETTER OFF GOING ANYWHERE ELSE. LIARS, SCAMMERS AND THIEVES.


Useful
1

Share

Advertisement

Lucia Zurbitu
TR
•
1 review
May 9, 2023
Rated 1 out of 5 stars
scammers, liars and thieves
I originally planned a trip to go get a hollywood smile and had to cancel due to a family emergency in my home country. The past 2 months have been an absolute nightmare trying to get the deposit I made back. Don't even bother requesting documentation as you'll never get anything. They could give 2 sh*ts about your situation and are only looking to steal from customers which is sad really. It's gotten to the point where i'm borderline harassing them everyday for a refund i was told i can get back at any time (i have pictures and recordings to prove it). this is a joke for a clinic and i highly recommend for any of you not to spend your good hard earned money on these thieves. refer to my google review for more detail.


Useful
3

Share

Johan Star
US
•
1 review
Feb 28, 2023
Rated 5 out of 5 stars
Two Thumbs Up
I recently had a hair transplant procedure done at Esvita Hair Transplant Company and I couldn't be happier with the results. From the initial consultation to the post-op follow-up, the entire experience was excellent. I don't know what Esvita means but it should mean choosing the right option.

The staff at Esvita were friendly and knowledgeable, answering all of my questions and addressing any concerns I had throughout the process. The facility was clean and modern, and I felt very comfortable throughout the entire procedure. I asked for their licences and they did show it me without any frowning upon such a request. Just wanted to test their nerves.

But most importantly, the results of my hair transplant are amazing. The procedure was quick and painless as it could get, and the team did a fantastic job of making sure that the grafts were placed in a way that looks natural and seamless. The density of my hair has improved significantly and I no longer feel self-conscious about my thinning hair.

Overall, I highly recommend these guys to anyone considering a hair transplant. The staff and facilities are top-notch, and the results speak for themselves. Thanks again to Esvita for giving me my confidence back!


Useful

Share

Selman Esen
TR
•
1 review
Jan 11, 2023
Rated 5 out of 5 stars
Perfect 👌👌

Useful

Share"""


def parse_reviews(text: str) -> list[dict]:
    reviews = []

    # Split by "Rated N out of 5 stars" pattern
    rating_pattern = re.compile(r'Rated (\d) out of 5 stars', re.IGNORECASE)

    # Find all rating positions
    matches = list(rating_pattern.finditer(text))

    noise = {
        'Useful', 'Share', 'Advertisement',
        'See if a website is trustworthy without leaving the page',
        'Verified', 'Reply from Esvita Clinic',
        '•'
    }

    for i, match in enumerate(matches):
        rating = int(match.group(1))

        # Get text before this rating (reviewer name is there)
        start = matches[i-1].end() if i > 0 else 0
        before = text[start:match.start()].strip()

        # Extract reviewer name: last non-noise, non-date, non-country line before rating
        before_lines = [l.strip() for l in before.split('\n') if l.strip()]

        name = 'Anonim'
        for line in reversed(before_lines):
            if (len(line) < 60
                and line not in noise
                and not re.match(r'^[A-Z]{2}$', line)  # country code
                and not re.match(r'^\d+\s+reviews?$', line)
                and not re.match(r'^(Updated\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', line)
            ):
                name = line
                break

        # Get text after rating
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        after = text[match.end():end].strip()

        # Remove noise lines from beginning and extract review text
        after_lines = after.split('\n')
        text_lines = []
        skip_next = False
        for line in after_lines:
            line_s = line.strip()
            if not line_s:
                if text_lines:
                    text_lines.append('')
                continue
            if line_s in noise or re.match(r'^\d+$', line_s):
                break  # end of review content
            if line_s.startswith('Reply from') or line_s.startswith('Esvita Clinic logo'):
                break
            text_lines.append(line_s)

        # Clean up: first line is often the title (truncated), rest is body
        # Remove trailing empty lines
        while text_lines and not text_lines[-1]:
            text_lines.pop()

        review_text = ' '.join(text_lines).strip()

        # Generate ID
        rid = hashlib.sha256(f"tp|{name}|{rating}".encode()).hexdigest()

        reviews.append({
            'review_id': rid,
            'reviewer_name': name,
            'rating': rating,
            'review_text': review_text,
        })

    # Deduplicate by review_id
    seen = {}
    for r in reviews:
        if r['review_id'] not in seen:
            seen[r['review_id']] = r
        else:
            # Keep the one with longer text
            if len(r['review_text']) > len(seen[r['review_id']]['review_text']):
                seen[r['review_id']] = r

    return list(seen.values())


async def post_to_api(reviews: list[dict]) -> dict:
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
                text = await resp.text()
                raise Exception(f"API error {resp.status}: {text}")
            return await resp.json()


async def main():
    reviews = parse_reviews(RAW_TEXT)
    print(f"Parsed {len(reviews)} reviews from paste")

    for r in reviews[:3]:
        print(f"  [{r['rating']}★] {r['reviewer_name']}: {r['review_text'][:60]}")

    result = await post_to_api(reviews)
    print(f"\nAPI: new={result.get('new')}, deleted={result.get('deleted')}, total={result.get('total')}")


if __name__ == '__main__':
    asyncio.run(main())
