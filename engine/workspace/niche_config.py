"""
engine/workspace/niche_config.py
=================================
Sprint 7: 25+ niches + كل دول MENA.
"""

# ══════════════════════════════════════════════
# NICHES — 25+ تخصص
# ══════════════════════════════════════════════

NICHE_CONFIG = {

    # ── Technology ─────────────────────────────
    "tech": {
        "label": "Tech / Software", "emoji": "💻",
        "keywords": ["software","developer","programming","API","open source","framework","cloud","DevOps","CI/CD","kubernetes"],
        "reddit_subs": ["programming","technology","webdev","devops","MachineLearning"],
        "google_news_query": "software technology developer tools",
        "sources_priority": ["hackernews","github_trending","devto","stackoverflow"],
    },
    "ai_startup": {
        "label": "AI / Startups", "emoji": "🤖",
        "keywords": ["AI","LLM","startup","GPT","machine learning","agents","RAG","vector database","foundation model","generative AI"],
        "reddit_subs": ["artificial","MachineLearning","startups","LocalLLaMA","OpenAI"],
        "google_news_query": "artificial intelligence startup LLM generative AI",
        "sources_priority": ["hackernews","producthunt","github_trending","twitter"],
    },
    "cybersecurity": {
        "label": "Cybersecurity", "emoji": "🔐",
        "keywords": ["cybersecurity","hacking","penetration testing","zero day","ransomware","CISO","SOC","threat intel","vulnerability","malware"],
        "reddit_subs": ["netsec","cybersecurity","hacking","AskNetsec","blueteamsec"],
        "google_news_query": "cybersecurity hacking data breach threat intelligence",
        "sources_priority": ["hackernews","reddit","google_news","twitter"],
    },
    "web3": {
        "label": "Web3 / Crypto / NFT", "emoji": "⛓",
        "keywords": ["crypto","blockchain","DeFi","NFT","Web3","Ethereum","Bitcoin","smart contract","DAO","tokenomics"],
        "reddit_subs": ["CryptoCurrency","ethereum","DeFi","NFT","web3"],
        "google_news_query": "cryptocurrency blockchain DeFi Web3 NFT",
        "sources_priority": ["reddit","twitter","google_news","youtube"],
    },

    # ── Business ───────────────────────────────
    "marketing": {
        "label": "Marketing / Content", "emoji": "📣",
        "keywords": ["marketing","content","SEO","social media","brand","engagement","viral","campaign","influencer","copywriting"],
        "reddit_subs": ["marketing","socialmedia","content_marketing","SEO","digital_marketing"],
        "google_news_query": "digital marketing content strategy social media",
        "sources_priority": ["instagram","tiktok","linkedin","twitter","reddit"],
    },
    "ecommerce": {
        "label": "E-commerce / Retail", "emoji": "🛒",
        "keywords": ["ecommerce","shopify","retail","dropshipping","marketplace","product","conversion","checkout","D2C","supply chain"],
        "reddit_subs": ["ecommerce","dropshipping","Entrepreneur","smallbusiness","shopify"],
        "google_news_query": "ecommerce retail online shopping trends",
        "sources_priority": ["reddit","producthunt","google_trends","google_news"],
    },
    "finance": {
        "label": "Finance / Fintech", "emoji": "💳",
        "keywords": ["fintech","crypto","blockchain","investment","banking","payments","DeFi","trading","stocks","NFT"],
        "reddit_subs": ["fintech","CryptoCurrency","investing","wallstreetbets","personalfinance"],
        "google_news_query": "fintech finance cryptocurrency investment banking",
        "sources_priority": ["reddit","hackernews","google_news","youtube"],
    },
    "saas": {
        "label": "SaaS / B2B", "emoji": "☁",
        "keywords": ["SaaS","B2B","subscription","product-led growth","PLG","churn","MRR","ARR","customer success","onboarding"],
        "reddit_subs": ["SaaS","Entrepreneur","startups","ProductManagement","CustomerSuccess"],
        "google_news_query": "SaaS B2B software product growth",
        "sources_priority": ["hackernews","producthunt","linkedin","reddit"],
    },

    # ── Lifestyle ──────────────────────────────
    "health": {
        "label": "Health / Medtech", "emoji": "🏥",
        "keywords": ["health","medtech","healthcare","wellness","biotech","telemedicine","fitness","mental health","pharma","AI health"],
        "reddit_subs": ["healthcare","health","medicine","Fitness","nutrition"],
        "google_news_query": "health medtech healthcare wellness biotech",
        "sources_priority": ["google_news","reddit","medium","youtube"],
    },
    "fitness": {
        "label": "Fitness / Sports", "emoji": "💪",
        "keywords": ["fitness","workout","gym","nutrition","CrossFit","running","bodybuilding","yoga","sports","athletic performance"],
        "reddit_subs": ["Fitness","weightlifting","running","nutrition","bodybuilding"],
        "google_news_query": "fitness sports workout nutrition health",
        "sources_priority": ["youtube","instagram","tiktok","reddit"],
    },
    "food": {
        "label": "Food / Restaurants", "emoji": "🍽",
        "keywords": ["food","restaurant","recipe","cuisine","chef","dining","food tech","delivery","meal prep","gourmet"],
        "reddit_subs": ["food","recipes","Cooking","GifRecipes","FoodPorn"],
        "google_news_query": "food restaurant cuisine recipe food tech",
        "sources_priority": ["instagram","tiktok","youtube","reddit"],
    },
    "travel": {
        "label": "Travel / Tourism", "emoji": "✈",
        "keywords": ["travel","tourism","destination","hotel","airline","backpacking","visa","travel hacks","digital nomad","hospitality"],
        "reddit_subs": ["travel","solotravel","digitalnomad","backpacking","flights"],
        "google_news_query": "travel tourism destination hotel airline",
        "sources_priority": ["youtube","instagram","reddit","google_news"],
    },
    "fashion": {
        "label": "Fashion / Beauty", "emoji": "👗",
        "keywords": ["fashion","style","luxury","streetwear","sustainable fashion","beauty","skincare","makeup","trends","outfit"],
        "reddit_subs": ["femalefashionadvice","malefashionadvice","streetwear","SkincareAddiction","makeupaddiction"],
        "google_news_query": "fashion beauty style luxury trends",
        "sources_priority": ["instagram","tiktok","pinterest","youtube"],
    },

    # ── Education & Knowledge ──────────────────
    "education": {
        "label": "Education / Edtech", "emoji": "🎓",
        "keywords": ["edtech","online learning","education","e-learning","LMS","curriculum","MOOCs","skills","training","bootcamp"],
        "reddit_subs": ["edtech","education","learnprogramming","OnlineLearning","Teachers"],
        "google_news_query": "edtech education online learning skills training",
        "sources_priority": ["youtube","medium","reddit","google_news","producthunt"],
    },
    "personal_dev": {
        "label": "Personal Development", "emoji": "🧠",
        "keywords": ["productivity","self improvement","habits","mindset","goal setting","journaling","morning routine","discipline","focus","growth"],
        "reddit_subs": ["getdisciplined","productivity","selfimprovement","nosurf","LifeAdvice"],
        "google_news_query": "personal development productivity mindset self improvement",
        "sources_priority": ["youtube","medium","reddit","instagram"],
    },

    # ── Real Estate & Construction ─────────────
    "real_estate": {
        "label": "Real Estate / Property", "emoji": "🏠",
        "keywords": ["real estate","property","mortgage","investment property","rental","REITs","housing market","PropTech","construction","interior design"],
        "reddit_subs": ["realestate","landlord","RealEstateInvesting","FirstTimeHomeBuyer","homeowners"],
        "google_news_query": "real estate property market housing mortgage",
        "sources_priority": ["reddit","google_news","linkedin","youtube"],
    },

    # ── Creative ───────────────────────────────
    "design": {
        "label": "Design / UX/UI", "emoji": "🎨",
        "keywords": ["design","UX","UI","figma","user research","product design","typography","branding","motion design","design system"],
        "reddit_subs": ["UXDesign","graphic_design","web_design","userexperience","designthought"],
        "google_news_query": "UX UI design figma product design branding",
        "sources_priority": ["dribbble","producthunt","medium","youtube"],
    },
    "gaming": {
        "label": "Gaming / Esports", "emoji": "🎮",
        "keywords": ["gaming","esports","game development","unity","unreal engine","indie game","streaming","twitch","game release","metaverse"],
        "reddit_subs": ["gaming","gamedev","pcgaming","esports","indiegaming"],
        "google_news_query": "gaming esports game development metaverse",
        "sources_priority": ["reddit","twitter","youtube","twitch"],
    },
    "media": {
        "label": "Media / Entertainment", "emoji": "🎬",
        "keywords": ["media","entertainment","streaming","Netflix","content creation","podcast","YouTube","influencer","viral video","production"],
        "reddit_subs": ["entertainment","television","movies","podcasts","Filmmakers"],
        "google_news_query": "media entertainment streaming content creation",
        "sources_priority": ["youtube","tiktok","reddit","twitter"],
    },

    # ── Specialized ───────────────────────────
    "legal": {
        "label": "Legal / LegalTech", "emoji": "⚖",
        "keywords": ["legal","law","legaltech","contract","compliance","IP","intellectual property","litigation","regulation","GDPR"],
        "reddit_subs": ["law","legaladvice","LegalTech","business","compliance"],
        "google_news_query": "legal legaltech law compliance regulation",
        "sources_priority": ["google_news","linkedin","medium","reddit"],
    },
    "logistics": {
        "label": "Logistics / Supply Chain", "emoji": "🚚",
        "keywords": ["logistics","supply chain","shipping","warehouse","last mile","3PL","freight","inventory","ERP","procurement"],
        "reddit_subs": ["logistics","supplychain","Trucking","warehouse","ecommerce"],
        "google_news_query": "logistics supply chain shipping freight warehouse",
        "sources_priority": ["linkedin","google_news","medium","reddit"],
    },
    "hr_recruiting": {
        "label": "HR / Recruiting", "emoji": "👔",
        "keywords": ["HR","recruiting","talent acquisition","remote work","DEI","employee experience","HR tech","compensation","onboarding","culture"],
        "reddit_subs": ["humanresources","recruitinghell","cscareerquestions","jobs","RemoteWork"],
        "google_news_query": "HR recruiting talent remote work human resources",
        "sources_priority": ["linkedin","reddit","medium","google_news"],
    },
    "agriculture": {
        "label": "Agriculture / AgriTech", "emoji": "🌾",
        "keywords": ["agriculture","agritech","farming","precision agriculture","IoT farming","vertical farming","food security","crop tech","irrigation","smart farming"],
        "reddit_subs": ["farming","agriculture","agtech","gardening","Homesteading"],
        "google_news_query": "agriculture agritech farming food technology",
        "sources_priority": ["google_news","medium","linkedin","reddit"],
    },
    "energy": {
        "label": "Energy / CleanTech", "emoji": "⚡",
        "keywords": ["energy","solar","renewable","cleantech","EV","battery","grid","climate tech","carbon","net zero"],
        "reddit_subs": ["energy","solar","electricvehicles","ClimateOffensive","sustainability"],
        "google_news_query": "energy renewable solar cleantech EV climate",
        "sources_priority": ["google_news","linkedin","medium","reddit"],
    },
    "mental_health": {
        "label": "Mental Health / Wellness", "emoji": "🧘",
        "keywords": ["mental health","therapy","anxiety","depression","mindfulness","wellness","psychology","CBT","self-care","burnout"],
        "reddit_subs": ["mentalhealth","Anxiety","depression","Mindfulness","therapy"],
        "google_news_query": "mental health wellness mindfulness therapy psychology",
        "sources_priority": ["reddit","medium","youtube","instagram"],
    },
}

NICHES = list(NICHE_CONFIG.keys())

NICHE_LABELS = {k: v["label"] for k, v in NICHE_CONFIG.items()}
NICHE_EMOJIS = {k: v["emoji"] for k, v in NICHE_CONFIG.items()}


# ══════════════════════════════════════════════
# MARKETS — كل دول MENA + Global
# ══════════════════════════════════════════════

MARKET_CONFIG = {
    # المشرق العربي
    "egypt":        {"label": "🇪🇬 مصر",          "lang": "ar", "region": "EG", "google_region": "egypt",                  "timezone": "Africa/Cairo"},
    "saudi":        {"label": "🇸🇦 السعودية",      "lang": "ar", "region": "SA", "google_region": "saudi_arabia",           "timezone": "Asia/Riyadh"},
    "uae":          {"label": "🇦🇪 الإمارات",      "lang": "ar", "region": "AE", "google_region": "united_arab_emirates",   "timezone": "Asia/Dubai"},
    "kuwait":       {"label": "🇰🇼 الكويت",        "lang": "ar", "region": "KW", "google_region": "kuwait",                 "timezone": "Asia/Kuwait"},
    "qatar":        {"label": "🇶🇦 قطر",           "lang": "ar", "region": "QA", "google_region": "qatar",                  "timezone": "Asia/Qatar"},
    "bahrain":      {"label": "🇧🇭 البحرين",       "lang": "ar", "region": "BH", "google_region": "bahrain",                "timezone": "Asia/Bahrain"},
    "oman":         {"label": "🇴🇲 عُمان",         "lang": "ar", "region": "OM", "google_region": "oman",                   "timezone": "Asia/Muscat"},
    "jordan":       {"label": "🇯🇴 الأردن",        "lang": "ar", "region": "JO", "google_region": "jordan",                 "timezone": "Asia/Amman"},
    "iraq":         {"label": "🇮🇶 العراق",        "lang": "ar", "region": "IQ", "google_region": "iraq",                   "timezone": "Asia/Baghdad"},
    "lebanon":      {"label": "🇱🇧 لبنان",         "lang": "ar", "region": "LB", "google_region": "lebanon",                "timezone": "Asia/Beirut"},
    "palestine":    {"label": "🇵🇸 فلسطين",        "lang": "ar", "region": "PS", "google_region": "palestine",              "timezone": "Asia/Gaza"},
    "syria":        {"label": "🇸🇾 سوريا",         "lang": "ar", "region": "SY", "google_region": "syria",                  "timezone": "Asia/Damascus"},
    "yemen":        {"label": "🇾🇪 اليمن",         "lang": "ar", "region": "YE", "google_region": "yemen",                  "timezone": "Asia/Aden"},

    # شمال أفريقيا
    "morocco":      {"label": "🇲🇦 المغرب",        "lang": "ar", "region": "MA", "google_region": "morocco",                "timezone": "Africa/Casablanca"},
    "algeria":      {"label": "🇩🇿 الجزائر",       "lang": "ar", "region": "DZ", "google_region": "algeria",                "timezone": "Africa/Algiers"},
    "tunisia":      {"label": "🇹🇳 تونس",          "lang": "ar", "region": "TN", "google_region": "tunisia",                "timezone": "Africa/Tunis"},
    "libya":        {"label": "🇱🇾 ليبيا",         "lang": "ar", "region": "LY", "google_region": "libya",                  "timezone": "Africa/Tripoli"},
    "sudan":        {"label": "🇸🇩 السودان",       "lang": "ar", "region": "SD", "google_region": "sudan",                  "timezone": "Africa/Khartoum"},
    "mauritania":   {"label": "🇲🇷 موريتانيا",     "lang": "ar", "region": "MR", "google_region": "mauritania",             "timezone": "Africa/Nouakchott"},
    "somalia":      {"label": "🇸🇴 الصومال",       "lang": "ar", "region": "SO", "google_region": "somalia",                "timezone": "Africa/Mogadishu"},

    # دول أخرى في المنطقة
    "turkey":       {"label": "🇹🇷 تركيا",         "lang": "tr", "region": "TR", "google_region": "turkey",                 "timezone": "Europe/Istanbul"},
    "iran":         {"label": "🇮🇷 إيران",         "lang": "fa", "region": "IR", "google_region": "iran",                   "timezone": "Asia/Tehran"},
    "pakistan":     {"label": "🇵🇰 باكستان",       "lang": "ur", "region": "PK", "google_region": "pakistan",               "timezone": "Asia/Karachi"},

    # عالمي
    "global":       {"label": "🌍 Global",          "lang": "en", "region": "US", "google_region": "united_states",          "timezone": "UTC"},
    "mena":         {"label": "🌐 MENA Region",      "lang": "ar", "region": "AE", "google_region": "united_arab_emirates",  "timezone": "Asia/Dubai"},
}

MARKETS = list(MARKET_CONFIG.keys())
MARKET_LABELS = {k: v["label"] for k, v in MARKET_CONFIG.items()}


# ══════════════════════════════════════════════
# SCRAPING PLATFORMS — للـ platform selector
# ══════════════════════════════════════════════

PLATFORM_CONFIG = {
    "reddit":       {"label": "Reddit",         "emoji": "🔴", "type": "community"},
    "hackernews":   {"label": "Hacker News",    "emoji": "🟠", "type": "tech"},
    "devto":        {"label": "Dev.to",         "emoji": "⚫", "type": "tech"},
    "medium":       {"label": "Medium",         "emoji": "🟢", "type": "blog"},
    "github":       {"label": "GitHub Trending","emoji": "⚫", "type": "tech"},
    "stackoverflow":{"label": "StackOverflow",  "emoji": "🟤", "type": "tech"},
    "youtube":      {"label": "YouTube",        "emoji": "🔴", "type": "video"},
    "producthunt":  {"label": "Product Hunt",   "emoji": "🟠", "type": "startup"},
    "google_news":  {"label": "Google News",    "emoji": "🔵", "type": "news"},
    "google_trends":{"label": "Google Trends",  "emoji": "🔵", "type": "trends"},
    "twitter":      {"label": "Twitter/X",      "emoji": "⚫", "type": "social"},
    "linkedin":     {"label": "LinkedIn",       "emoji": "🔵", "type": "professional"},
    "tiktok":       {"label": "TikTok",         "emoji": "⚫", "type": "social"},
    "instagram":    {"label": "Instagram",      "emoji": "🟣", "type": "social"},
}

PLATFORMS = list(PLATFORM_CONFIG.keys())
PLATFORM_LABELS = {k: v["label"] for k, v in PLATFORM_CONFIG.items()}


# ══════════════════════════════════════════════
# PROMPT BUILDERS
# ══════════════════════════════════════════════

def get_niche_prompt(niche: str, markets: list, trends: list) -> str:
    cfg   = NICHE_CONFIG.get(niche, NICHE_CONFIG["tech"])
    label = cfg["label"]
    mkt   = ", ".join(MARKET_CONFIG.get(m, {}).get("label", m) for m in markets)
    topics = "\n".join(f"{i+1}. {t}" for i, t in enumerate(trends[:10]))

    return f"""
You are a viral content strategist specializing in {label} for {mkt} markets.

Based on these trending topics in {label}:
{topics}

Generate a complete content strategy for {label} professionals targeting {mkt}:

1. 10 viral hooks tailored for {label} audience
2. 10 post ideas (include platform: LinkedIn/Instagram/Twitter/TikTok)
3. 5 thread ideas for technical depth
4. 5 short video ideas (30-60 seconds)

Focus on {label} pain points, tools, and trends.
Be specific, not generic. Avoid buzzwords.
Return structured text with clear headers.
"""


def get_deep_search_prompt(niche: str, markets: list) -> str:
    cfg   = NICHE_CONFIG.get(niche, NICHE_CONFIG["tech"])
    label = cfg["label"]
    kws   = ", ".join(cfg["keywords"][:5])
    mkt   = ", ".join(MARKET_CONFIG.get(m, {}).get("label", m) for m in markets)

    return f"""
You are a trend analyst for {label} in {mkt} markets.

Find 20 emerging trends in {label} right now.
Focus on keywords like: {kws}

Return ONLY a numbered list:
1. [trend title]
2. [trend title]
...

No descriptions, no extra text, just the numbered list.
"""


def get_competitor_suggestions_prompt(niche: str, markets: list) -> str:
    """يولّد prompt لاقتراح منافسين بناءً على الـ niche."""
    cfg   = NICHE_CONFIG.get(niche, NICHE_CONFIG["tech"])
    label = cfg["label"]
    mkt   = ", ".join(MARKET_CONFIG.get(m, {}).get("label", m) for m in markets)

    return f"""
List the top 10 most prominent brands, companies, or content creators in {label} 
that are active in {mkt} markets.

Return ONLY a JSON array like this:
[
  {{"name": "Company Name", "url": "https://website.com", "type": "brand"}},
  ...
]

Types: brand | publication | influencer | platform
No extra text, just the JSON array.
"""