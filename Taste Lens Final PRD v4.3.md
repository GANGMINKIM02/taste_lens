# Taste Lens Final PRD v4.3

## 0. 제품 개요

Taste Lens는 별도의 음식 추천 앱이 아니라 **기존 배달앱 위에 추가되는 개인 취향 기반 Food Discovery Layer**다.

사용자는 최초 이용 시 10회의 음식 Pairwise Choice를 수행하고, 이를 통해 장기적인 개인 Taste Vector `U_base`를 생성한다.

그 이후에는 기존 배달앱과 동일한 방식으로 서비스를 이용한다.

홈 화면:

```text
음식 카테고리

[한식] [중식] [일식] [치킨]
[피자] [분식] [카페·디저트] [기타]

────────────────────────

✨ 취향렌즈
지금 내 입맛에 맞는 음식 찾기
```

Taste Lens 진입:

```text
오늘은 어떻게 찾아볼까요?

[✨ 알아서 추천]

[한식] [중식]
[일식] [치킨]
[피자] [분식]
[카페·디저트] [기타]
```

최종 탐색 구조:

```text
Taste
↓
Food
↓
Restaurant
↓
Menu
```

추천 시 사용자의 장기 Taste에 현재 장소·시간대·날씨를 반영한다.

```text
U_base
+
Place
+
Time
+
Weather
=
U_current
```

---

# 1. 문제 정의

기존 배달앱은 일반적으로:

```text
카테고리
↓
식당
↓
메뉴
↓
평점·리뷰 확인
↓
선택
```

순으로 탐색한다.

하지만 평점, 리뷰 수, 주문 수, 인기순, 배달시간 등의 지표는:

> 다른 사람이 얼마나 만족했는가

를 알려줄 수는 있어도:

> **지금 이 음식 또는 메뉴가 내 입맛에 얼마나 잘 맞는가**

를 직접 알려주지는 못한다.

Taste Lens는 기존 추천 기준을 대체하지 않고:

```text
Personal Taste Fit
```

이라는 추가적인 판단 축을 제공한다.

---

# 2. 제품 모델링 원칙

Taste Lens는 인간의 음식 취향 전체를 정확한 하나의 숫자로 표현한다고 주장하지 않는다.

Taste Lens가 모델링하는 것은:

> **음식 선택에 영향을 주는 여러 요인 중 Taste Preference**

다.

즉:

```text
Spicy = .72
```

는 절대적인 인간의 매운맛 선호 점수가 아니라:

> 현재까지 관찰된 선택·주문·리뷰 Evidence를 기반으로 추정한 상대적 Taste Position

이다.

마찬가지로:

```text
내 취향 94%
```

는:

> 이 메뉴를 좋아할 확률 94%

가 아니다.

정확한 내부 의미는:

> **현재 User Taste와 Menu Taste Vector 사이의 6차원 공간상 Similarity**

다.

---

# 3. 공통 Taste Space

모든 Taste 관련 객체는 동일한 6차원 공간을 사용한다.

```python
TASTE_AXES = [
    "sweet",
    "salty",
    "sour",
    "umami",
    "spicy",
    "nutty"
]
```

| Axis | 의미 |
|---|---|
| sweet | 단맛 |
| salty | 짠맛 |
| sour | 신맛 |
| umami | 감칠맛 |
| spicy | 매운맛 |
| nutty | 고소함 |

모든 Axis:

```text
0.0 ≤ score ≤ 1.0
```

---

# 4. 핵심 Vector 정의

## 4.1 Food Vector

```text
F_food
```

음식 종류 자체의 대표적인 초기 Taste Prior.

---

## 4.2 RestaurantMenu Vector

```text
R_menu
```

특정 Restaurant이 판매하는 특정 Menu의 Taste Vector.

같은 김치찌개라도 식당마다 다른 `R_menu`를 가진다.

---

## 4.3 U_base

사용자의 장기적인 개인 Taste Preference.

---

## 4.4 U_current

현재 추천 시점의 Context를 적용한 임시 Taste Vector.

```python
U_current =
clip(
    U_base
    + Delta_place
    + Delta_time
    + Delta_weather,
    0,
    1
)
```

`U_current`는 영구적인 사용자 Taste로 저장하지 않는다.

---

# 5. Food Seed Dataset

MVP에서는 총 70개의 Seed Food를 사용한다.

| Category | 수 |
|---|---:|
| 한식 | 14 |
| 중식 | 8 |
| 일식 | 8 |
| 치킨 | 8 |
| 피자 | 8 |
| 분식 | 8 |
| 카페·디저트 | 8 |
| 기타·글로벌 | 8 |
| **총합** | **70** |

---

# 5.1 한식 14개

```text
제육볶음
김치찌개
순두부찌개
비빔밥
물냉면
불고기
된장찌개
삼겹살
육개장
설렁탕
부대찌개
오징어볶음
비빔냉면
해물파전
```

---

# 5.2 중식 8개

```text
짜장면
짬뽕
마파두부
탕수육
마라탕
양꼬치
볶음밥
유산슬
```

---

# 5.3 일식 8개

```text
돈코츠라멘
쇼유라멘
돈가스
초밥
규동
가라아게
우동
메밀소바
```

---

# 5.4 치킨 8개

```text
후라이드치킨
양념치킨
간장치킨
매운양념치킨
마늘치킨
허니치킨
파닭
숯불치킨
```

---

# 5.5 피자 8개

```text
페퍼로니피자
치즈피자
고구마피자
불고기피자
하와이안피자
포테이토피자
고르곤졸라피자
핫치킨피자
```

---

# 5.6 분식 8개

```text
떡볶이
라볶이
순대
튀김
김밥
쫄면
어묵
만두
```

---

# 5.7 카페·디저트 8개

```text
초콜릿케이크
치즈케이크
크로플
도넛
팥빙수
아이스크림
소금빵
베이글
```

---

# 5.8 기타·글로벌 8개

```text
쌀국수
팟타이
타코
햄버거
파스타
샐러드
커리
케밥
```

---

# 6. Food Vector 초기 산정

Food Vector는 관능평가 Ground Truth가 아니라:

> Recommendation Prior

로 정의한다.

각 Food × Taste Axis에 대해 세 요소를 평가한다.

```text
I = Ingredient Strength
D = Sensory Dominance
P = Processing / Cooking Amplification
```

각 값:

```text
0
0.25
0.50
0.75
1.00
```

Raw Score:

```text
FoodRaw
=
0.45 × I
+
0.40 × D
+
0.15 × P
```

이후 동일 Axis에서 70개 음식의 상대 순서를 검토해 Calibration한다.

핵심 목표:

```text
Absolute Truth
X

Relative Rank Consistency
O
```

---

# 7. Restaurant-first Dataset

Restaurant Dataset은 Food마다 독립적으로 식당을 생성하지 않는다.

실제 배달 플랫폼처럼:

> **하나의 Restaurant이 여러 Menu를 판매한다.**

예:

```text
청춘찌개
│
├─ 김치찌개
├─ 순두부찌개
├─ 부대찌개
├─ 된장찌개
└─ 제육볶음
```

동시에 하나의 Food는 여러 Restaurant에서 판매된다.

```text
김치찌개
│
├─ 청춘찌개
├─ 서울밥상
├─ 한성국밥
└─ 우리집백반
```

따라서:

```text
Food : Restaurant
=
N : M
```

관계이며 `restaurant_menus`가 이를 연결한다.

---

# 8. MVP Restaurant Seed 규모

| Category | Restaurant 수 | 식당당 Taste Lens 대상 메뉴 |
|---|---:|---:|
| 한식 | 10 | 5~8 |
| 중식 | 5 | 4~6 |
| 일식 | 5 | 4~6 |
| 치킨 | 4 | 5~8 |
| 피자 | 4 | 5~8 |
| 분식 | 4 | 5~7 |
| 카페·디저트 | 4 | 5~7 |
| 기타·글로벌 | 5 | 4~6 |
| **총합** | **약 41** | **약 210~250 RestaurantMenu** |

---

# 9. Restaurant Seed Constraints

```text
1. Restaurant당 최소 4개 RestaurantMenu

2. 한식 Restaurant은 평균 6개 이상
   Taste Lens 대상 메뉴 보유

3. 각 Seed Food는 최소 3개 Restaurant에서 판매

4. 핵심 한식 Food는 최소 4개 Restaurant에서 판매

5. 동일 Food라도 Restaurant마다
   별도 RestaurantMenu Vector 보유

6. Menu 구성은 Restaurant Type과
   현실적인 조합을 따라야 함

7. 서로 관련 없는 Category 메뉴를
   무작위로 섞지 않음
```

---

# 10. Restaurant Type

한식 예:

```text
찌개·백반
고기·볶음
국밥·탕
냉면
종합한식
```

중식:

```text
중화요리
마라
양꼬치
```

일식:

```text
라멘
돈가스
초밥
일식종합
```

Restaurant Type은 Seed Menu 구성의 현실성을 유지하는 용도로 사용한다.

---

# 11. 한식 Restaurant 예시

## 청춘찌개

```text
김치찌개
순두부찌개
부대찌개
된장찌개
제육볶음
```

## 서울밥상

```text
제육볶음
불고기
비빔밥
된장찌개
해물파전
```

## 한성국밥

```text
설렁탕
육개장
김치찌개
순두부찌개
```

## 불맛공방

```text
제육볶음
오징어볶음
불고기
비빔밥
```

## 냉면마을

```text
물냉면
비빔냉면
불고기
해물파전
```

---

# 12. RestaurantMenu 초기 Vector

RestaurantMenu는 초기에는 해당 Food Prior에서 시작한다.

```text
R_initial = F_food
```

예:

```text
김치찌개 Food Prior

Sweet   .25
Salty   .65
Sour    .55
Umami   .78
Spicy   .62
Nutty   .18
```

Review Evidence가 축적되면:

```text
청춘찌개 김치찌개

Sweet   .30
Salty   .68
Sour    .58
Umami   .80
Spicy   .72
Nutty   .17
```

```text
서울밥상 김치찌개

Sweet   .22
Salty   .61
Sour    .67
Umami   .76
Spicy   .55
Nutty   .19
```

처럼 분화한다.

---

# 13. 최초 Pairwise Onboarding

총 10문항.

```text
Q1~Q6
Coverage Phase

Q7~Q10
Adaptive Refinement
```

UI:

```text
Q3 / 10

[제육볶음 이미지]

VS

[돈코츠라멘 이미지]

지금 둘 중 하나를 먹는다면?
```

---

# 14. Category-independent Pairwise

Pairwise 질문 생성 시 Category 자체는 Taste Feature로 사용하지 않는다.

예:

```text
제육볶음 vs 초밥
떡볶이 vs 돈코츠라멘
삼겹살 vs 치즈케이크
마라탕 vs 고구마피자
```

목표:

```text
어떤 카테고리를 좋아하는가
X

어떤 Taste Profile에 끌리는가
O
```

---

# 15. Coverage Pair Selection

Food A, B:

```text
D_AB,k =
|F_A,k - F_B,k|
```

Contrast:

```text
Contrast(A,B)
=
Σ w_k × |F_A,k-F_B,k|
```

초기:

```text
w_k = 1
```

---

# 16. Coverage Balance

```text
Coverage_k
=
Σ previous_pairs
|F_A,k-F_B,k|
```

다음 질문의 Axis Weight:

```text
w_k =
1 / (0.1 + Coverage_k)
```

이미 충분히 관찰한 Axis의 우선순위를 낮춘다.

---

# 17. Pair Repeat Constraint

Q1~Q6:

```text
동일 Food 최대 1회
```

Q1~Q10 전체:

```text
동일 Food 최대 2회
동일 Pair 최대 1회
```

70개 음식의 가능한 unordered pair:

```text
70 × 69 / 2
=
2,415 pairs
```

---

# 18. Pairwise User Model

초기:

```text
U =
[.5,.5,.5,.5,.5,.5]
```

Distance:

```python
d(U,F) =
sqrt(
    mean(
        (U-F) ** 2
    )
)
```

사용자가 A 선택:

```text
z =
β ×
[d(U,B)-d(U,A)]
```

```text
P(A)
=
1 / (1+exp(-z))
```

MVP:

```text
β = 8
```

---

# 19. Pairwise Loss

```text
L_pair
=
-Σ log(P(actual_selected_food))
```

Neutral Prior:

```text
U_neutral =
[.5,.5,.5,.5,.5,.5]
```

Total Loss:

```text
L_total
=
L_pair
+
λ ||U-U_neutral||²
```

MVP:

```text
λ = .05
```

---

# 20. User Vector Optimization

Bounded Coordinate Descent.

Step:

```text
.20
.10
.05
.02
.01
.005
.001
```

각 Axis에서:

```text
U_k + step
U_k - step
```

을 평가.

Loss가 낮아지는 방향으로 이동한다.

항상:

```text
clip(U_k,0,1)
```

적용.

---

# 21. Adaptive Q7~Q10

Q1~Q6 후:

```text
U_temp
```

계산.

Axis별 Evidence:

```text
Evidence_k
=
Σ |F_selected,k-F_rejected,k|
```

Evidence가 적은 Axis를 Target으로 선택한다.

Candidate Pair:

```text
TargetContrast =
|F_A,k-F_B,k|
```

현재 User 기준:

```text
dA = d(U_temp,F_A)
dB = d(U_temp,F_B)
```

Utility:

```text
Utility
=
TargetContrast
-
0.7 × |dA-dB|
```

즉:

> Taste 차이는 크지만 현재 User Vector 기준으로 답이 너무 뻔하지 않은 Pair

를 선택한다.

---

# 22. U_base 생성

10문항 종료:

```text
U_base =
[
sweet,
salty,
sour,
umami,
spicy,
nutty
]
```

DB 저장.

사용자 UI:

```text
매운맛과 감칠맛을 특히 좋아해요.
짭짤한 맛도 선호하는 편이에요.
신맛은 상대적으로 덜 선호해요.
```

---

# 23. Taste Lens Scope

Taste Lens:

```text
[✨ 알아서 추천]

[한식]
[중식]
[일식]
[치킨]
[피자]
[분식]
[카페·디저트]
[기타]
```

Category는:

```text
Taste Feature
X

Candidate Filter
O
```

---

# 24. Category Recommendation

예:

```text
한식 선택
→ 14개 Food
```

```text
중식 선택
→ 8개 Food
```

각 Food와 `U_current`를 비교한다.

---

# 25. 알아서 추천

```text
Candidate Pool
=
All 70 Foods
```

Top 5 제공.

Diversity Constraint:

```text
Top 5 내
동일 Category 최대 2개
```

---

# 26. Context-aware Taste

최종 추천 Vector:

```python
U_current =
clip(
    U_base
    + Delta_place
    + Delta_time
    + Delta_weather,
    0,
    1
)
```

---

# 27. Place Context

주소 원문 자체를 Taste Feature로 사용하지 않는다.

생활 장소 유형으로 변환:

```text
home
school
work
other
```

Cold Start:

```text
Delta_home   = 0
Delta_school = 0
Delta_work   = 0
Delta_other  = 0
```

---

# 28. Place Personalization

전체 주문 평균:

```text
M_all
```

해당 장소 주문 평균:

```text
M_place
```

```text
Raw =
M_place - M_all
```

Reliability:

```text
r_place =
n_place / (n_place+10)
```

Scale:

```text
scale_place = .40
```

최종:

```text
Delta_place
=
r_place
× .40
× clip(
M_place-M_all,
-.15,
+.15
)
```

---

# 29. Time Context

```text
05:00–10:59 morning
11:00–13:59 lunch
14:00–16:59 afternoon
17:00–21:59 dinner
22:00–04:59 late_night
```

Cold Start:

```text
late_night

Salty +.02
Spicy +.02
```

나머지 0.

Reliability:

```text
r_time =
n_time/(n_time+12)
```

Scale:

```text
scale_time = .30
```

Final:

```text
Delta_time =
(1-r_time) × Delta_global_time
+
r_time × .30 ×
clip(
M_time-M_all,
-.15,
+.15
)
```

---

# 30. Weather Context

Weather Type:

```text
rain
hot
cold
normal
unknown
```

Open-Meteo 사용.

Priority:

```text
Rain condition
→ rain

temperature ≥ 28℃
→ hot

temperature ≤ 8℃
→ cold

otherwise
→ normal
```

Rain을 우선 처리한다.

---

# 31. Weather Global Prior

Rain:

```text
Spicy +.03
Umami +.03
```

Hot:

```text
Sour +.03
Spicy -.02
```

Cold:

```text
Umami +.03
Spicy +.02
```

Normal:

```text
0
```

---

# 32. Weather Personalization

```text
r_weather =
n_weather/(n_weather+20)
```

```text
scale_weather = .20
```

Final:

```text
Delta_weather =
(1-r_weather) × Delta_global_weather
+
r_weather × .20 ×
clip(
M_weather-M_all,
-.15,
+.15
)
```

---

# 33. Context Summary

| Context | Scale | Prior |
|---|---:|---:|
| Place | .40 | 10 |
| Time | .30 | 12 |
| Weather | .20 | 20 |

Context Raw Delta:

```text
±.15
```

Clip.

---

# 34. Food Match

```python
food_distance =
sqrt(
    mean(
        (U_current-F_food) ** 2
    )
)
```

```python
food_match =
clip(
    1-food_distance,
    0,
    1
)
```

UI:

```text
취향 일치 94%
```

---

# 35. Food Recommendation UI

예:

```text
한식 추천

[제육볶음 사진]
제육볶음
✨ 취향 일치 94%

[육개장 사진]
육개장
✨ 취향 일치 91%

[김치찌개 사진]
김치찌개
✨ 취향 일치 88%
```

Food Card 필수 요소:

```text
Food Image
Food Name
Taste Match %
Taste Tags 2~3개
```

---

# 36. Food → Restaurant

사용자가:

```text
김치찌개
```

선택.

Backend:

```text
restaurant_menus
WHERE food_id = KIMCHI_STEW
```

조회.

결과:

```text
청춘찌개 김치찌개
서울밥상 김치찌개
한성국밥 김치찌개
우리집백반 김치찌개
```

---

# 37. Restaurant Ranking

각 해당 RestaurantMenu:

```python
restaurant_match =
clip(
    1 -
    sqrt(
        mean(
            (U_current-R_menu) ** 2
        )
    ),
    0,
    1
)
```

예:

```text
김치찌개 판매 식당

청춘찌개        95%
서울밥상        91%
한성국밥        87%
우리집백반      84%
```

---

# 38. Restaurant List UI

Food 선택 후 식당 목록은 반드시 식당 대표사진과 함께 표시한다.

예:

```text
────────────────────────

[청춘찌개 대표사진]

청춘찌개
✨ 김치찌개 내 취향 95%
★ 4.8
25~35분
배달비 2,000원

────────────────────────

[서울밥상 대표사진]

서울밥상
✨ 김치찌개 내 취향 91%
★ 4.7
30~40분
무료배달

────────────────────────
```

Card 필수 요소:

```text
Restaurant Representative Image
Restaurant Name
Selected Food Taste Match
Rating
Delivery Time
Delivery Fee
Optional Review Count
```

---

# 39. Restaurant Detail

식당 진입 후 기존 배달앱 UX를 유지한다.

상단:

```text
Restaurant Representative Image

Restaurant Name
Rating
Review Count
Delivery Time
Delivery Fee
Minimum Order
Favorite
```

Menu Section:

```text
대표 메뉴
찌개
볶음
면
사이드
음료
```

---

# 40. Restaurant 내 여러 Menu

예:

```text
청춘찌개

김치찌개
순두부찌개
부대찌개
된장찌개
제육볶음
```

김치찌개를 보고 들어왔더라도 해당 식당의 다른 메뉴를 모두 탐색할 수 있다.

---

# 41. Menu-level Taste Match

각 Menu Card:

```text
김치찌개                [김치찌개 사진]
✨ 내 취향 95%
깊고 칼칼한 돼지고기 김치찌개
10,000원
```

```text
순두부찌개              [순두부찌개 사진]
✨ 내 취향 91%
얼큰한 순두부와 해산물
10,000원
```

```text
부대찌개                [부대찌개 사진]
✨ 내 취향 86%
햄과 소시지가 들어간 진한 찌개
12,000원
```

Match:

```python
menu_distance =
sqrt(
    mean(
        (U_current-R_menu) ** 2
    )
)
```

```python
menu_match =
clip(
    1-menu_distance,
    0,
    1
)
```

---

# 42. Menu Sorting

기존 Seller Menu Order는 유지한다.

Taste Score로 강제 재정렬하지 않는다.

```text
대표메뉴
인기메뉴
메인
사이드
```

기존 구조 유지.

Taste Lens는:

```text
✨ 내 취향 XX%
```

만 추가한다.

Optional:

```text
✨ 내 취향 추천 Top 3
```

상단 영역은 향후 추가 가능.

---

# 43. Image Asset Strategy

이미지 자산은 공모전 Demo의 현실감과 서비스 이해도를 높이는 핵심 UX 요소다.

전체 이미지 자산은:

```text
Food Image
Restaurant Representative Image
RestaurantMenu Image
```

세 계층으로 구분한다.

---

# 44. Food Image 규칙

Seed Food:

```text
70개
```

각 Food는 반드시 고유한 대표 이미지를 가진다.

```text
70 Food
=
70 Unique Food Images
```

DB:

```text
food_image_url
```

사용 위치:

```text
Pairwise Onboarding
Food Recommendation
Food Detail / Selection
```

동일 Food의 대표 이미지는 Food 단계에서 일관되게 사용한다.

---

# 45. Restaurant Representative Image

Restaurant 약:

```text
41개
```

각 Restaurant은 반드시 다른 대표사진을 가진다.

```text
41 Restaurant
=
41 Unique Restaurant Representative Images
```

DB:

```text
image_url
```

또는 명확성을 위해:

```text
restaurant_image_url
```

사용 위치:

```text
Food → Restaurant List
Restaurant Detail Header
Order History Restaurant Context
```

---

# 46. RestaurantMenu Image

전체 RestaurantMenu:

```text
약 210~250개
```

모든 Menu에는:

```text
menu_image_url
```

필드가 존재한다.

하지만 210~250개 메뉴 모두를 완전히 다른 원본 이미지로 준비할 필요는 없다.

권장 Unique Menu Image Pool:

```text
100~150개
```

---

# 47. Menu Image Reuse Policy

RestaurantMenu Image는 제한적으로 재사용을 허용한다.

단 다음 규칙을 반드시 지킨다.

```text
1. 동일 Restaurant 상세 화면 안에서는
   같은 이미지 반복 사용 금지

2. 동일 Food를 판매하는 Restaurant 비교 흐름에서
   가능하면 서로 다른 Menu Image 사용

3. Demo Critical Path에 등장하는
   모든 RestaurantMenu Image는 고유 이미지 사용

4. 인접 Card에서 동일 이미지 반복 금지

5. 같은 Restaurant에서
   서로 다른 Menu가 같은 이미지를 쓰지 않음

6. 동일 Food 이미지 재사용 시
   충분히 떨어진 Restaurant/Menu에 배치
```

---

# 48. Demo Critical Path Image Rule

현장 발표에서 실제로 이동할 핵심 경로:

```text
Pairwise
↓
Taste Lens
↓
한식
↓
김치찌개
↓
Restaurant List
↓
청춘찌개
↓
Restaurant Detail
↓
여러 Menu
↓
Order
↓
Review
```

이 경로 안에 등장하는 모든:

```text
Food Image
Restaurant Image
Menu Image
```

는 고유 이미지로 구성한다.

즉 시연 중에는 사용자가 동일 이미지를 반복해서 보는 일이 없도록 한다.

---

# 49. 시연상 Image Uniqueness 목표

전체 Database 차원에서는 일부 Menu Image가 재사용될 수 있다.

그러나 사용자 관점에서는:

```text
Food마다 사진이 다름
Restaurant마다 대표사진이 다름
한 Restaurant 안의 Menu마다 사진이 다름
Restaurant 비교 화면의 사진도 다름
```

으로 인식되도록 구성한다.

즉 목표는:

> **Physical Asset Uniqueness 100%가 아니라 Perceived UX Uniqueness 100%**

다.

---

# 50. Image Asset 권장 수량

| Asset | 전체 객체 수 | 권장 Unique Image |
|---|---:|---:|
| Food | 70 | 70 |
| Restaurant | 약 41 | 41 |
| RestaurantMenu | 210~250 | 100~150 |
| **총 Unique Images** | - | **약 211~261** |

---

# 51. Image Format

모든 이미지:

```text
WebP 권장
```

AVIF 지원 시 선택적 사용 가능.

PNG 원본 대량 사용 금지.

---

# 52. Image Resolution

## Food

```text
600~800 px
```

권장.

## Restaurant

```text
800~1200 px
```

권장.

## RestaurantMenu

```text
400~600 px
```

권장.

---

# 53. Image Compression

권장 Quality:

```text
70~80%
```

목표 파일 용량:

### Food

```text
80~150 KB / image
```

### Restaurant

```text
150~250 KB / image
```

### Menu

```text
80~150 KB / image
```

---

# 54. Image Asset 예상 총 용량

70 Food:

```text
약 5.6~10.5 MB
```

41 Restaurant:

```text
약 6.2~10.3 MB
```

100~150 Unique Menu:

```text
약 8~22.5 MB
```

예상:

```text
약 20~43 MB
```

실제 프로젝트 목표:

```text
30~50 MB
```

수준으로 관리한다.

---

# 55. Storage Architecture

이미지 Binary 자체는 DB에 저장하지 않는다.

Supabase Storage 또는 CDN 사용.

예:

```text
storage/

foods/
restaurants/
menus/
```

DB에는 URL만 저장한다.

```text
food_image_url

restaurant_image_url

menu_image_url
```

이미지 생성은 Runtime에서 수행하지 않는다.

```text
Image Generation Tool
↓
사전 생성
↓
WebP 최적화
↓
Supabase Storage 업로드
↓
DB image_url 저장
↓
Next.js에서 조회
```

즉 실제 사용자 요청 시 이미지 생성 API를 호출하지 않고, 이미 생성·저장된 Asset을 CDN/Storage URL로 제공한다.

---

# 56. Next.js Image Optimization

Frontend에서는 가능하면:

```text
Next.js <Image>
```

사용.

Lazy Loading 적용.

Restaurant Detail 진입 전에는 해당 Restaurant의 모든 Menu 이미지를 미리 로딩하지 않는다.

필요한 화면의 자산만 Load한다.

---

# 57. Image Fallback

이미지가 불러와지지 않은 경우:

```text
Generic Food Placeholder
Generic Restaurant Placeholder
Generic Menu Placeholder
```

사용 가능.

단:

> 정상 Demo 데이터에서는 Placeholder가 노출되지 않아야 한다.

---

# 58. Order Learning

일반 주문:

```text
eta_order = .05
```

```python
U_after =
clip(
    .95 * U_before
    + .05 * R_ordered,
    0,
    1
)
```

---

# 59. Reorder Learning

```text
eta_reorder = .08
```

```python
U_after =
.92 * U_before
+
.08 * R_ordered
```

재주문은 일반 주문보다 강한 Preference Signal로 본다.

---

# 60. Quantity Rule

```text
1 Order Event
=
1 Taste Choice Event
```

같은 Menu를 여러 개 주문해도 Taste Update를 수량만큼 반복하지 않는다.

---

# 61. Order Snapshot

주문 시:

```text
user_vector_before
user_vector_after

vector_version_before
vector_version_after

repeat_order
taste_update_applied
```

저장.

---

# 62. 주문 완료 UX

Taste 변화는 자동으로 강제 표시하지 않는다.

```text
주문 완료

[주문 내역 보기]
[홈으로 가기]

────────────────

✨ 이번 주문이
내 취향에 어떻게 반영됐을까요?

[내 취향 변화 보기]
```

핵심 원칙:

```text
Learning = Automatic
Explanation = Optional
```

---

# 63. Order Taste Change UI

버튼 클릭 시:

```text
이번 주문이 취향에 조금 반영됐어요.

매운맛
68 → 69

감칠맛
70 → 71
```

Display:

```text
abs(U_after-U_before) ≥ .005
```

이고:

```text
round(after×100)
!=
round(before×100)
```

인 Axis 우선 표시.

---

# 64. Review Entry Flow

Review 작성 경로:

```text
마이페이지
↓
주문 내역
↓
완료된 주문
↓
[리뷰 작성]
```

조건:

```text
order_status = completed
```

---

# 65. Review UI

MVP는 Menu-level Review를 기본으로 한다.

```text
청춘찌개

[김치찌개 사진]

김치찌개

음식은 어떠셨나요?

☆ ☆ ☆ ☆ ☆

“다른 집보다 덜 달고 꽤 매웠어요.
저는 조금 더 매워도 좋을 것 같아요.”

[리뷰 등록]
```

---

# 66. Rating과 Taste 분리

Rating:

```text
Satisfaction / Quality Signal
```

Taste Vector 직접 업데이트:

```text
X
```

Taste Evidence:

```text
Review Text
```

에서 추출한다.

---

# 67. Solar Pro 4 Review Analysis

```text
Review Text
↓
Solar Pro 4
↓
Structured Evidence
↓
Schema Validation
↓
Numerical Update Engine
```

Output:

```json
{
  "menu_taste_claims": [],
  "user_preference_claims": []
}
```

---

# 68. Menu Taste Claim

예:

```text
“다른 집보다 덜 달아요.”
```

```json
{
  "axis": "sweet",
  "level": -1,
  "comparative": true,
  "confidence": 0.91,
  "evidence_text": "다른 집보다 덜 달아요"
}
```

이 Claim은 해당 `restaurant_menu_id`만 업데이트한다.

---

# 69. User Preference Claim

```text
“저는 조금 더 매운 게 좋아요.”
```

```json
{
  "axis": "spicy",
  "direction": "prefer_more",
  "confidence": 0.88,
  "evidence_text": "조금 더 매운 게 좋아요"
}
```

User Preference에만 사용.

---

# 70. Review Level

```text
-2 = 매우 약함
-1 = 다소 약함
 0 = 명확한 변화 없음
+1 = 다소 강함
+2 = 매우 강함
```

Taste와 무관한:

```text
맛있어요
양 많아요
친절해요
배달 빨라요
```

는 Taste Claim으로 만들지 않는다.

---

# 71. Comparative Weight

```text
q =
level
×
(
1.2 if comparative
else 1.0
)
```

---

# 72. Review Confidence

Unique Review 수:

```text
n
```

```text
confidence =
n/(n+10)
```

예:

```text
1  → .09
5  → .33
10 → .50
30 → .75
```

---

# 73. RestaurantMenu Learning

동일 Food 판매 Menu들을 Peer Group으로 비교한다.

Axis Percentile:

```text
p ∈ [0,1]
```

Center:

```text
c =
2p-1
```

Delta:

```text
Delta_restaurant
=
.15
× confidence
× c
```

Final:

```text
R_menu =
clip(
F_food + Delta_restaurant,
0,
1
)
```

Food Prior 대비 최대 변화:

```text
±.15
```

---

# 74. Review-based User Learning

조건:

```text
claim_type = user_preference

confidence ≥ .75

valid axis

explicit preference evidence
```

Learning Rate:

```text
eta_review = .02
```

---

# 75. Review User Update

예:

```text
U_spicy = .68
```

Review:

```text
“조금 더 매워도 좋았어요.”
```

Target:

```text
target =
min(
U_spicy + .10,
1
)
```

Update:

```text
U_after =
.98U_before
+
.02target
```

예:

```text
.680 → .682
```

---

# 76. Review Impact UX

리뷰 등록 후 자동 노출하지 않는다.

```text
리뷰가 등록됐어요.

[주문 내역으로 돌아가기]

────────────────

✨ 이 리뷰가 내 취향에
어떻게 반영됐을까요?

[리뷰 취향 변화 보기]
```

Review 변화 UI:

```text
작성한 표현:
“조금 더 매워도 좋았어요.”

매운맛
68.0 → 68.2
```

---

# 77. User Preference 없는 Review

```text
“국물이 진하고 많이 매웠어요.”
```

Menu Taste Evidence:

```text
O
```

User Preference:

```text
X
```

User Taste Update:

```text
0
```

UI:

```text
이번 리뷰에서는
내 취향 점수가 바뀌지 않았어요.

메뉴의 맛 정보는 학습했지만,
개인 선호에 대한 명확한 표현은
없었어요.
```

---

# 78. Review Status

```text
pending
processing
completed
failed
```

Retry:

```text
same review_id
```

중복 업데이트 방지:

```text
restaurant_update_applied
user_update_applied
```

---

# 79. Database Schema

## users

```text
user_id
created_at
updated_at
```

---

## user_profiles

```text
user_id

sweet
salty
sour
umami
spicy
nutty

vector_version
baseline_at

created_at
updated_at
```

---

## foods

```text
food_id
name
category

food_image_url

sweet
salty
sour
umami
spicy
nutty

vector_version
source
rationale

created_at
updated_at
```

---

## restaurants

```text
restaurant_id
name

category
restaurant_type

restaurant_image_url

rating
review_count

delivery_minutes
delivery_fee
minimum_order

created_at
updated_at
```

---

## restaurant_menus

```text
restaurant_menu_id

restaurant_id
food_id

menu_name
menu_description
menu_image_url

price

sweet
salty
sour
umami
spicy
nutty

menu_section

is_representative
is_popular
is_available

vector_version
evidence_count
source

created_at
updated_at
```

---

## onboarding_responses

```text
user_id
question_index

left_food_id
right_food_id
selected_food_id

created_at
```

---

## orders

```text
order_id
user_id
restaurant_menu_id

place_type
time_segment
weather_type

context_snapshot

user_vector_before
user_vector_after

vector_version_before
vector_version_after

repeat_order
taste_update_applied

status

created_at
completed_at
```

---

## reviews

```text
review_id

order_id
user_id

restaurant_id
restaurant_menu_id

rating
review_text

status

user_vector_before
user_vector_after

user_update_applied
restaurant_update_applied

created_at
updated_at
```

---

## review_evidence

```text
evidence_id
review_id

claim_type
axis

level
direction
comparative

confidence
evidence_text

model
prompt_version

created_at
```

---

## recommendations

```text
recommendation_id
user_id

scope
category

candidate_ids
scores

context_snapshot

user_vector_snapshot
vector_version

selected_food_id
selected_restaurant_id
selected_restaurant_menu_id

created_at
```

---

# 80. Context Snapshot

Order:

```json
{
  "place_type": "home",
  "time_segment": "late_night",
  "weather_type": "rain",
  "temperature": 18.4
}
```

---

# 81. User Vector Version

```text
Onboarding
→ v1

Order
→ v2

Review Preference
→ v3

Reorder
→ v4
```

Recommendation은 항상 당시 사용한 Vector Version을 저장한다.

---

# 82. Recommendation Logging

저장 대상:

```text
U_current
context

candidate foods
candidate scores

selected food

candidate restaurants
selected restaurant

candidate menu
selected menu

vector_version
```

---

# 83. System Architecture

Taste Lens MVP는 하나의 GitHub Repository를 기준으로 관리하며, Production Demo는 Vercel에 배포한다.

```text
GitHub Repository
        │
        │ push / merge
        ▼
Vercel Project
        │
        ├─ Next.js / React
        │      │
        │      └─ /
        │
        └─ FastAPI
               │
               └─ /api/*
                    │
                    ├─ NumPy / Python Numerical Engine
                    ├─ Solar Pro 4 via Upstage API
                    ├─ Supabase PostgreSQL
                    ├─ Supabase Storage
                    └─ Open-Meteo
```

Application 내부 논리 구조는 다음과 같다.

```text
Existing Delivery App UX
        │
        ▼
Next.js / React
        │
        ▼
FastAPI Backend
   │          │
   ▼          ▼
NumPy      Solar Pro 4
   │          │
   └────┬─────┘
        ▼
Supabase PostgreSQL
        │
        ├─ Supabase Storage
        │
        └─ Open-Meteo
```

Production에서는 Frontend와 Backend를 같은 Vercel Project에서 운영하고, Frontend는 동일 Origin의 `/api` 경로로 FastAPI에 접근한다.

```text
Browser
   │
   ├─ /
   │   → Next.js
   │
   └─ /api/*
       → FastAPI
```

이 구조를 통해 Production에서 별도 Backend Domain을 관리하지 않고 CORS 및 API Base URL 설정을 단순화한다.

---

# 84. Solar Pro 4 역할

Solar가 수행:

```text
Review
→ Menu Taste Evidence

Review
→ Explicit User Preference

User Taste
→ Natural Language Explanation

Recommendation
→ Natural Language Explanation

Food Seed
→ Rationale / Audit Support
```

Solar가 수행하지 않음:

```text
Numeric Distance

Ranking

Context Numeric Calculation

User Vector Arithmetic

Restaurant Aggregate Calculation

DB Transaction
```

원칙:

> **Solar interprets. Python calculates.**

---

# 85. Hyperparameter Summary

| Parameter | MVP |
|---|---:|
| Taste Axis | 6 |
| Food Seed | 70 |
| Korean Food | 14 |
| Other Category Food | 각 8 |
| Restaurant | 약 41 |
| RestaurantMenu | 약 210~250 |
| Unique Food Images | 70 |
| Unique Restaurant Images | 약 41 |
| Unique Menu Images | 100~150 |
| 예상 Unique Image 총량 | 211~261 |
| Image Asset 목표 용량 | 30~50MB |
| Pairwise | 10 |
| Coverage Q | 6 |
| Adaptive Q | 4 |
| β | 8 |
| λ | .05 |
| Adaptive Difficulty Penalty | .7 |
| Order LR | .05 |
| Reorder LR | .08 |
| Review LR | .02 |
| Review Confidence Threshold | .75 |
| Restaurant Max Delta | ±.15 |
| Review Confidence Prior | 10 |
| Comparative Multiplier | 1.2 |
| Place Scale | .40 |
| Place Prior | 10 |
| Time Scale | .30 |
| Time Prior | 12 |
| Weather Scale | .20 |
| Weather Prior | 20 |
| Context Raw Delta Clip | ±.15 |
| Order Impact Display | .005 |
| Auto Top-5 Same Category | 최대 2 |
| Food당 Restaurant | 최소 3 |
| 핵심 한식 Food당 Restaurant | 최소 4 |
| Restaurant당 Menu | 최소 4 |

모든 숫자는 MVP Initial Hyperparameter이며 사용자 데이터 기반 Calibration 대상으로 둔다.

---

# 86. 최종 User Journey

```text
최초 로그인
↓
Pairwise ×10
↓
U_base 생성
↓
일반 배달앱 Home
↓
✨ Taste Lens
↓
Auto / Category
↓
현재 장소 + 시간대 + 날씨
↓
U_current
↓
Food Recommendation
↓
Food Image + Taste %
↓
Food 선택
↓
해당 Food 판매 Restaurant 조회
↓
Restaurant 대표사진이 포함된 Restaurant List
↓
Restaurant별 Selected Food Taste %
↓
Restaurant 선택
↓
Restaurant 대표사진
↓
기존 Restaurant Detail
↓
Restaurant의 여러 Menu
↓
각 Menu Image + 내 취향 %
↓
Menu 선택
↓
Cart
↓
Order
↓
User Taste 자동 학습
↓
[원할 때 주문 취향 변화 보기]
↓
주문 완료
↓
마이페이지
↓
주문 내역
↓
Review
↓
Solar Pro 4
↓
RestaurantMenu Taste Learning
+
Optional User Preference Learning
↓
[원할 때 리뷰 취향 변화 보기]
↓
Next Recommendation
```

---

# 87. 전체 Learning Loop

```text
Pairwise
↓
U_base
↓
Context
↓
U_current
↓
Food Match
↓
RestaurantMenu Match
↓
Order
↓
User Learning
```

동시에:

```text
RestaurantMenu Prior
↓
Review
↓
Solar Pro 4
↓
Taste Evidence
↓
RestaurantMenu Learning
↓
다음 사용자의 Taste Match 개선
```

두 Loop가 동시에 작동한다.

---

# 88. 최종 UX 원칙

```text
Learning
=
Automatic

Explanation
=
Optional
```

사용자가 AI를 관리할 필요가 없다.

초기에는:

> 몇 번의 음식 선택으로 취향을 추정한다.

이후에는:

> 평소처럼 주문하고 리뷰하면 조용히 학습한다.

추천 순간에는:

> 장소·시간·날씨까지 반영한다.

필요한 경우에만:

> 이번 주문이나 리뷰가 내 취향에 어떻게 반영됐는지 확인한다.

---

# 89. 이미지 UX 원칙

이미지 전략의 핵심은:

> **모든 데이터 객체가 실제로 100% 다른 파일을 가져야 하는 것이 아니라, 사용자가 탐색하는 화면에서는 모두 서로 다른 것처럼 보여야 한다.**

따라서:

```text
Food
→ 70개 모두 고유

Restaurant
→ 약 41개 모두 고유

RestaurantMenu
→ 100~150개 Unique Pool 활용
→ 약 210~250 Menu에 전략적 매핑
```

한다.

그리고:

```text
Demo Critical Path
=
100% 고유 이미지
```

원칙을 적용한다.

---

# 90. 최종 제품 정의

**Taste Lens는 총 70개의 Seed Food를 Sweet·Salty·Sour·Umami·Spicy·Nutty의 6차원 Taste Space에 표현하고, 최초 이용 시 10회의 Pairwise Choice를 통해 사용자의 장기 Taste Vector `U_base`를 추정한다. 이후 현재 주소를 home·school·work·other의 생활 장소로 해석하고 시간대와 날씨를 함께 반영해 추천 순간의 `U_current`를 생성한다.**

**Restaurant Dataset은 Food별로 독립적인 식당을 만드는 것이 아니라 실제 배달 플랫폼처럼 약 41개의 Restaurant이 각자의 업종에 맞는 여러 RestaurantMenu를 판매하는 Restaurant-first 구조로 구성한다. 총 약 210~250개의 RestaurantMenu를 구성하고 하나의 Food는 최소 3개 이상의 Restaurant에서 중복 판매되며, 핵심 한식 Food는 최소 4개 이상의 Restaurant에서 판매된다.**

**사용자가 Food를 선택하면 해당 Food를 판매하는 Restaurant들을 Restaurant 대표사진과 함께 목록으로 제공하고, 각 Restaurant이 판매하는 해당 Food의 RestaurantMenu Vector와 U_current를 비교해 개인 Taste Match를 계산한다. Restaurant 진입 후에는 기존 배달앱의 식당 상세 UX를 유지하면서 해당 Restaurant이 판매하는 여러 Menu의 사진·이름·설명·가격 옆에 각 메뉴별 `내 취향 %`를 표시한다.**

**Food 70개에는 각각 고유한 대표 Food Image를 사용하고, 약 41개의 Restaurant에도 각각 고유한 Restaurant Representative Image를 사용한다. 약 210~250개의 RestaurantMenu에는 100~150개의 Unique Menu Image Pool을 전략적으로 배정하되 동일 Restaurant 내부, 동일 Food의 Restaurant 비교 화면, 그리고 현장 Demo Critical Path에서는 이미지가 반복되지 않도록 한다. 이를 통해 전체 이미지 자산은 약 211~261개의 Unique Image와 약 30~50MB 수준으로 유지하면서도 사용자에게는 모든 주요 화면이 서로 다른 이미지로 보이도록 구성한다.**

**주문 및 재주문은 User Taste를 자동으로 학습하고, 주문 완료 이후의 Review는 Solar Pro 4가 비정형 자연어에서 RestaurantMenu Taste Evidence와 명시적인 User Preference를 분리해 추출한다. RestaurantMenu Taste Description은 해당 Menu Vector를 보정하고 명시적인 개인 Preference만 User Taste에 낮은 가중치로 반영한다. Order와 Review에 따른 Taste 변화는 자동으로 강제 표시하지 않고 사용자가 원하는 경우에만 확인하도록 한다.**

**MVP 소스코드는 하나의 GitHub Repository에서 관리하고, Production Demo는 Vercel에 배포한다. Vercel에서는 Next.js Frontend를 `/`, FastAPI Backend를 `/api/*`로 동일 Project와 Origin에서 운영한다. Supabase PostgreSQL·Supabase Storage·Upstage Solar Pro 4·Open-Meteo는 FastAPI에서만 접근하며, `SUPABASE_SECRET_KEY`와 `UPSTAGE_API_KEY` 같은 Secret은 Frontend Bundle에 포함하지 않는다.**

**Taste Lens의 핵심은 주관적인 음식 취향에 절대적인 정답을 부여하는 것이 아니라, 사용자의 반복적인 선택·주문 행동·현재 상황·명시적 언어 표현을 동일한 Taste Space에서 점진적으로 학습하고, 동시에 RestaurantMenu의 실제 Taste도 리뷰를 통해 학습함으로써 `Taste → Food → Restaurant → Menu` 전체 탐색 과정에 Personal Taste Fit을 제공하는 Closed-loop Personalization Layer를 구현하는 것이다.**
---

# 91. Deployment & Release Architecture

## 91.1 Source Control

Taste Lens의 전체 Source of Truth는 하나의 GitHub Repository로 관리한다.

권장 Repository 구조:

```text
taste-lens/
├─ app/ or web/
├─ api/
├─ assets/
├─ scripts/
├─ tests/
├─ README.md
├─ DEPLOYMENT.md
├─ .env.example
└─ package / Python dependency files
```

개발 흐름:

```text
Local Development
↓
Git Commit
↓
GitHub Push
↓
Pull Request / main merge
↓
Vercel Build
↓
Production Deployment
```

MVP에서는 `main` Branch를 Production 기준 Branch로 사용한다.

---

## 91.2 Vercel Deployment Model

Taste Lens는 GitHub Repository를 Vercel Project와 연결한다.

Deployment 단위는 Frontend와 Backend를 분리한 두 개의 별도 서비스가 아니라 하나의 Vercel Project를 기본으로 한다.

```text
Vercel Project

/
→ Next.js / React

/api/*
→ FastAPI
```

FastAPI Entry Point는 Vercel Python Runtime과 호환되는 형태로 구성한다.

예:

```text
api/index.py
```

Production Frontend는 동일 Origin의 `/api`를 호출한다.

```text
NEXT_PUBLIC_API_BASE_URL=/api
```

이를 통해 Production 환경에서 Frontend와 Backend 사이의 별도 Domain 설정을 최소화한다.

---

# 92. Environment Variable Standard

환경변수 이름은 Project 전체에서 아래 Canonical Name만 사용한다.

## 92.1 Backend Variables

```env
SUPABASE_URL=
SUPABASE_SECRET_KEY=
SUPABASE_ASSET_BUCKET=taste-lens-assets

UPSTAGE_API_KEY=
UPSTAGE_API_BASE_URL=https://api.upstage.ai/v1
UPSTAGE_MODEL=solar-pro4

OPEN_METEO_ENABLED=true
CORS_ORIGINS=http://localhost:3000
```

## 92.2 Frontend Variables

Local Development:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Vercel Production:

```env
NEXT_PUBLIC_API_BASE_URL=/api
```

## 92.3 Secret Handling

다음 값은 반드시 Server-side Secret으로 관리한다.

```text
SUPABASE_SECRET_KEY
UPSTAGE_API_KEY
```

다음 위치에 포함하지 않는다.

```text
Client-side JavaScript
NEXT_PUBLIC_* Secret
GitHub Commit
Public Repository
Static Asset
Frontend Bundle
```

실제 Secret을 `.env.example`에 기록하지 않는다.

`.env.example`에는 Variable Name과 비어 있는 Placeholder만 유지한다.

---

# 93. External Service Responsibilities

## 93.1 Supabase

Supabase는 다음을 담당한다.

```text
PostgreSQL
→ User / Food / Restaurant / Menu / Order / Review / Recommendation 데이터

Storage
→ Food Image
→ Restaurant Representative Image
→ RestaurantMenu Image
```

Image Binary는 PostgreSQL에 저장하지 않고 Storage에 저장한다.

---

## 93.2 Upstage Solar Pro 4

Upstage API를 통해 Solar Pro 4를 호출한다.

Environment:

```text
UPSTAGE_API_KEY
UPSTAGE_API_BASE_URL
UPSTAGE_MODEL
```

Solar 역할은 기존 원칙을 유지한다.

```text
Solar interprets.
Python calculates.
```

Solar는 Review Text를 Structured Evidence로 변환하지만 Recommendation Ranking, Numerical Distance, Context Vector Arithmetic 및 DB Transaction은 수행하지 않는다.

---

## 93.3 Open-Meteo

Open-Meteo는 Weather Context 획득에 사용한다.

```text
Browser Location
↓
Latitude / Longitude
↓
FastAPI
↓
Open-Meteo
↓
rain / hot / cold / normal
```

Latitude/Longitude 자체는 Taste Feature로 저장하지 않는다.

---

# 94. Image Production Pipeline

이미지는 서비스 Runtime에서 생성하지 않는다.

개발 단계에서 외부 Image Generation Model을 이용해 사전 생성한다.

기본 목표:

```text
Food Image
70 Unique

Restaurant Representative Image
41 Unique

RestaurantMenu Image Pool
100~150 Unique

MVP Target
120 Unique Menu Images

Total Target
약 231 Unique Images
```

Production Pipeline:

```text
Image Manifest
↓
External Image Generation Model
↓
Generated Images
↓
WebP Optimization
↓
Supabase Storage
↓
Public Image URL
↓
Database URL Mapping
↓
Next.js Image Rendering
```

이미지 생성 Model은 Runtime Dependency가 아니다.

즉 사용자가 Recommendation을 요청할 때 Image Generation API를 호출하지 않는다.

---

# 95. CI / Build Validation

GitHub Push 이후 최소한 다음 검증을 수행한다.

```text
Python Syntax / Compile
↓
Python Unit Test
↓
Seed Constraint Validation
↓
Image Manifest Validation
↓
Frontend Type Check
↓
Next.js Build
↓
Vercel Deployment
```

가능한 경우 GitHub Actions를 이용해 Pull Request 또는 `main` Push 시 자동 검증한다.

CI 실패 시 Production Deployment 이전에 원인을 수정한다.

---

# 96. Deployment Verification

Vercel Deployment 후 다음 Endpoint와 화면을 확인한다.

## 96.1 Backend Health

```text
GET /api/health
```

확인 대상:

```text
FastAPI Running
Supabase Configuration
Upstage Configuration
```

Secret 자체의 값은 Response에 노출하지 않는다.

---

## 96.2 Frontend

확인:

```text
Home
Pairwise Onboarding
Taste Lens
Recommendation
Restaurant List
Restaurant Detail
Order
Order History
Review
```

---

## 96.3 External Integration

Production Environment에서 실제로 확인한다.

```text
Supabase Read
Supabase Write
Supabase Storage Image Load
Open-Meteo
Upstage Solar Pro 4
```

---

# 97. Production E2E Acceptance Test

최종 Production Build는 아래 전체 Flow가 성공해야 완료로 본다.

```text
New User
↓
Pairwise ×10
↓
U_base
↓
Taste Lens
↓
Context
↓
U_current
↓
Food Recommendation
↓
Food 선택
↓
Restaurant Recommendation
↓
Restaurant 선택
↓
Menu 탐색
↓
Menu 선택
↓
Order
↓
User Taste Learning
↓
Order History
↓
Review
↓
Solar Pro 4
↓
RestaurantMenu Learning
↓
Optional User Preference Learning
↓
Next Recommendation
```

Acceptance Criteria:

```text
Frontend Build PASS
FastAPI PASS
Supabase Read/Write PASS
Supabase Storage PASS
Open-Meteo PASS
Solar Pro 4 PASS
Pairwise PASS
Recommendation PASS
Order Learning PASS
Review Learning PASS
Image UX PASS
Full E2E PASS
```

---

# 98. Deployment Security Principles

Production에서는 다음 원칙을 적용한다.

```text
1. Secret은 Vercel Server Environment에만 저장
2. SUPABASE_SECRET_KEY를 Client에 노출하지 않음
3. UPSTAGE_API_KEY를 Client에 노출하지 않음
4. GitHub Repository에 실제 Secret Commit 금지
5. Frontend는 FastAPI를 통해 External Service 접근
6. Health Endpoint는 Configuration 여부만 반환
7. Log에 Secret 값 출력 금지
8. Production Image는 Supabase Storage URL 사용
```

---

# 99. 최종 Delivery Definition

Taste Lens MVP의 최종 제출물은 다음으로 정의한다.

```text
1. GitHub Repository
2. Vercel Production Deployment
3. Next.js Frontend
4. FastAPI Backend
5. Supabase PostgreSQL Schema
6. Supabase Storage Image Assets
7. Food / Restaurant / RestaurantMenu Seed
8. Pairwise Recommendation Engine
9. Context-aware Recommendation Engine
10. Order / Reorder Learning
11. Solar Pro 4 Review Analysis
12. Review-based Menu / User Learning
13. Image Asset Manifest
14. Image Optimization / Upload Script
15. Environment Variable Example
16. Deployment Guide
17. E2E Validation Result
```

최종 완료 기준은 단순히 Source Code가 존재하는 것이 아니라:

```text
GitHub Push
+
Vercel Deployment
+
External API Integration
+
Supabase Integration
+
Production E2E PASS
```

까지 완료된 상태다.

---

# 100. 최종 제품 정의 v4.3

**Taste Lens는 70개의 Seed Food를 6차원 Taste Space에 표현하고, 10회의 Pairwise Choice를 통해 `U_base`를 추정한 뒤 장소·시간·날씨 Context를 적용한 `U_current`를 기반으로 Food → Restaurant → Menu 전체 탐색 과정에 Personal Taste Fit을 제공하는 Food Discovery Layer다.**

**Restaurant-first 구조를 통해 약 41개의 Restaurant과 약 210~250개의 RestaurantMenu를 구성하고, 주문·재주문·Review를 통해 User Taste와 RestaurantMenu Taste를 점진적으로 학습한다. Solar Pro 4는 Review의 비정형 언어를 Structured Taste Evidence로 해석하고, Numerical Calculation과 Ranking은 Python Engine이 담당한다.**

**이미지는 Runtime에서 생성하지 않고 Food 70개, Restaurant 약 41개, RestaurantMenu용 100~150개의 Unique Image Pool을 사전 생성하여 WebP로 최적화한 뒤 Supabase Storage에 저장한다. Application에서는 DB에 저장된 Image URL을 통해 필요한 Asset만 Lazy Load한다.**

**Source Code는 하나의 GitHub Repository에서 관리하고, Production Demo는 하나의 Vercel Project에 배포한다. Next.js Frontend는 `/`, FastAPI Backend는 `/api/*`에서 동작하며, Supabase PostgreSQL·Supabase Storage·Upstage Solar Pro 4·Open-Meteo는 FastAPI를 통해 접근한다. `SUPABASE_SECRET_KEY`와 `UPSTAGE_API_KEY`는 Vercel Server Environment에만 저장한다.**

**최종 MVP 완료 기준은 GitHub Push, Vercel Deployment, Supabase 및 External API Integration, Image Asset 연결, 그리고 최초 Pairwise부터 Recommendation → Order → Review → 다음 Recommendation까지의 Production E2E Test가 모두 PASS한 상태다.**
