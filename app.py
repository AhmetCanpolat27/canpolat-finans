import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import requests
import xml.etree.ElementTree as ET
import os

try:
    import google.generativeai as genai
except:
    genai = None

try:
    from streamlit_autorefresh import st_autorefresh
except:
    st_autorefresh = None


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(page_title="CANPOLAT FİNANS", layout="wide", page_icon="🦅")

AI_AKTIF = False

if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        AI_AKTIF = True
    except:
        AI_AKTIF = False


st.markdown("""
<style>
.main { background-color: #0e1117; }
h1 { color: #ffd700; font-family: 'Trebuchet MS', sans-serif; }
div[data-testid="stMetric"] {
    background-color: #1f2937;
    border: 1px solid #374151;
    padding: 10px;
    border-radius: 10px;
}
.badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    margin-left: 5px;
}
.badge-up { background-color: #065f46; color: #34d399; }
.badge-down { background-color: #7f1d1d; color: #fca5a5; }
.badge-flat { background-color: #374151; color: #d1d5db; }

div.stButton > button {
    padding: 0px 5px;
    min-height: 30px;
    height: 30px;
    line-height: 1;
    border: 1px solid #4b5563;
}

.depth-container {
    width: 100%;
    background-color: #374151;
    border-radius: 5px;
    height: 25px;
    display: flex;
    overflow: hidden;
    margin-top: 5px;
}
.depth-buy {
    background-color: #00c853;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: bold;
    color: black;
}
.depth-sell {
    background-color: #d50000;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: bold;
    color: white;
}

div[data-testid="stTextInput"] > div > div > input {
    background-color: #1f2937;
    color: white;
    border: 1px solid #4b5563;
}
</style>
""", unsafe_allow_html=True)


def simdi_tr():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))

tr_saat = simdi_tr()
borsa_acik_mi = False

if tr_saat.weekday() < 5:
    if (9 <= tr_saat.hour < 18) or (tr_saat.hour == 18 and tr_saat.minute <= 30):
        borsa_acik_mi = True

# 15 dk bir yenile
if st_autorefresh:
    st_autorefresh(interval=900000, key="yenileme")


if "secilen_kod" not in st.session_state:
    st.session_state.secilen_kod = "THYAO.IS"

if "favoriler" not in st.session_state:
    st.session_state.favoriler = []


HAM_LISTE = [
    "GC=F", "SI=F", "USDTRY=X",
    "AEFES.IS", "AGHOL.IS", "AHGAZ.IS", "AKBNK.IS", "AKCNS.IS", "AKFGY.IS", "AKFYE.IS", "AKSA.IS", "AKSEN.IS", "ALARK.IS",
    "ALBRK.IS", "ALFAS.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "ASUZU.IS", "AYDEM.IS", "BAGFS.IS", "BERA.IS", "BIMAS.IS",
    "BIOEN.IS", "BRSAN.IS", "BRYAT.IS", "BUCIM.IS", "CANTE.IS", "CCOLA.IS", "CEMTS.IS", "CIMSA.IS", "CWENE.IS", "DOAS.IS",
    "DOHOL.IS", "ECILC.IS", "ECZYT.IS", "EGEEN.IS", "EKGYO.IS", "ENJSA.IS", "ENKAI.IS", "EREGL.IS", "EUPWR.IS", "EUREN.IS",
    "FROTO.IS", "GARAN.IS", "GENIL.IS", "GESAN.IS", "GLYHO.IS", "GSDHO.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HEKTS.IS",
    "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISFIN.IS", "ISGYO.IS", "ISMEN.IS", "IZMDC.IS", "KARSN.IS", "KCAER.IS", "KCHOL.IS",
    "KONTR.IS", "KONYA.IS", "KORDS.IS", "KOZAA.IS", "KOZAL.IS", "KRDMD.IS", "KZBGY.IS", "MAVI.IS", "MGROS.IS", "MIATK.IS",
    "ODAS.IS", "OTKAR.IS", "OYAKC.IS", "PENTA.IS", "PETKM.IS", "PGSUS.IS", "PSGYO.IS", "QUAGR.IS", "SAHOL.IS", "SASA.IS",
    "SISE.IS", "SKBNK.IS", "SMRTG.IS", "SNGYO.IS", "SOKM.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TOASO.IS",
    "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUKAS.IS", "TUPRS.IS", "TURSG.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS",
    "YEOTK.IS", "YKBNK.IS", "YYLGD.IS", "ZOREN.IS"
]

ISIM_SOZLUGU = {
    "GC=F": "GRAM ALTIN",
    "SI=F": "GRAM GÜMÜŞ",
    "USDTRY=X": "DOLAR/TL",
    "THYAO.IS": "THY",
    "ASELS.IS": "ASELSAN",
    "BIMAS.IS": "BIM",
    "EREGL.IS": "EREGLI",
    "TUPRS.IS": "TUPRAS",
    "AKBNK.IS": "AKBANK",
    "GARAN.IS": "GARANTI",
    "YKBNK.IS": "YAPI KREDI",
    "ISCTR.IS": "IS BANKASI",
    "SAHOL.IS": "SABANCI HOLDING",
    "FROTO.IS": "FORD OTO",
    "TOASO.IS": "TOFAS",
    "KCHOL.IS": "KOC HOLDING",
    "SASA.IS": "SASA",
    "HEKTS.IS": "HEKTAS",
    "SISE.IS": "SISECAM",
    "PETKM.IS": "PETKIM",
    "PGSUS.IS": "PEGASUS",
    "ASTOR.IS": "ASTOR",
    "KONTR.IS": "KONTROLMATIK",
    "ENJSA.IS": "ENERJISA",
    "ALARK.IS": "ALARKO",
    "ODAS.IS": "ODAS",
    "KOZAL.IS": "KOZA ALTIN",
    "KRDMD.IS": "KARDEMIR D",
    "ARCLK.IS": "ARCELIK",
    "VESTL.IS": "VESTEL",
    "EUPWR.IS": "EUROPOWER",
    "CWENE.IS": "CW ENERJI",
    "SMRTG.IS": "SMART GUNES",
    "MGROS.IS": "MIGROS",
    "TCELL.IS": "TURKCELL",
    "TTKOM.IS": "TURK TELEKOM",
    "EKGYO.IS": "EMLAK KONUT",
    "OYAKC.IS": "OYAK CIMENTO",
    "GUBRF.IS": "GUBRE FAB.",
    "DOHOL.IS": "DOGAN HOLDING",
    "SOKM.IS": "SOK MARKET",
    "ULKER.IS": "ULKER",
    "AEFES.IS": "ANADOLU EFES"
}


def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


@st.cache_data(ttl=900)
def liste_ozeti_getir(semboller):
    sonuc = {}

    for s in semboller:
        try:
            df = yf.Ticker(s).history(period="5d", auto_adjust=False)

            if df.empty or "Close" not in df.columns or len(df["Close"].dropna()) < 2:
                sonuc[s] = 0.0
                continue

            close = df["Close"].dropna()
            degisim = ((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100
            sonuc[s] = degisim
        except:
            sonuc[s] = 0.0

    return sonuc


def google_rss_haberleri(arama_terimi):
    try:
        url = f"https://news.google.com/rss/search?q={arama_terimi}&hl=tr&gl=TR&ceid=TR:tr"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        if response.status_code != 200:
            return []

        root = ET.fromstring(response.content)
        haberler = []

        for item in root.findall(".//item")[:5]:
            title = item.find("title")
            link = item.find("link")
            pubDate = item.find("pubDate")

            haberler.append({
                "title": title.text if title is not None else "",
                "link": link.text if link is not None else "",
                "pubDate": pubDate.text if pubDate is not None else ""
            })

        return haberler
    except:
        return []


def gemini_piyasa_ozeti(basliklar_listesi, hisse):
    if not AI_AKTIF:
        return "AI kapalı"

    try:
        basliklar_metni = "\n".join([f"- {b}" for b in basliklar_listesi])
        prompt = f"{hisse} için bu haberleri kısa tek paragrafta özetle:\n{basliklar_metni}"

        modeller = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]

        for m in modeller:
            try:
                model = genai.GenerativeModel(m)
                response = model.generate_content(prompt)
                if response and hasattr(response, "text"):
                    return response.text.strip()
            except:
                continue

        return "AI özeti alınamadı"
    except:
        return "AI özeti alınamadı"


@st.cache_data(ttl=900)
def detay_veri(sembol, tip, zaman):
    try:
        df = yf.Ticker(sembol).history(period=zaman, auto_adjust=False)

        if df.empty:
            return pd.DataFrame()

        try:
            df.index = pd.to_datetime(df.index).tz_localize(None)
        except:
            try:
                df.index = pd.to_datetime(df.index)
            except:
                pass

        if sembol in ["GC=F", "SI=F"]:
            usd = yf.Ticker("USDTRY=X").history(period=zaman, auto_adjust=False)

            if usd.empty:
                return pd.DataFrame()

            try:
                usd.index = pd.to_datetime(usd.index).tz_localize(None)
            except:
                try:
                    usd.index = pd.to_datetime(usd.index)
                except:
                    pass

            df = df.join(usd["Close"].rename("kur"), how="left").ffill().bfill()

            if tip == "TL (₺)":
                for c in ["Open", "High", "Low", "Close"]:
                    df[c] = (df[c] * df["kur"]) / 31.1034768
            else:
                for c in ["Open", "High", "Low", "Close"]:
                    df[c] = df[c] / 31.1034768

        elif tip == "Dolar ($)" and ".IS" in sembol:
            usd = yf.Ticker("USDTRY=X").history(period=zaman, auto_adjust=False)

            if usd.empty:
                return pd.DataFrame()

            try:
                usd.index = pd.to_datetime(usd.index).tz_localize(None)
            except:
                try:
                    usd.index = pd.to_datetime(usd.index)
                except:
                    pass

            df = df.join(usd["Close"].rename("kur"), how="left").ffill().bfill()

            for c in ["Open", "High", "Low", "Close"]:
                df[c] = df[c] / df["kur"]

        return df

    except:
        return pd.DataFrame()


@st.cache_data(ttl=900)
def hesapla_hacim_analizi(sembol):
    try:
        df_int = yf.download(sembol, period="1d", interval="1m", progress=False, auto_adjust=False)

        if df_int.empty:
            return 0, 0

        buy = df_int.loc[df_int["Close"] >= df_int["Open"], "Volume"].sum()
        sell = df_int.loc[df_int["Close"] < df_int["Open"], "Volume"].sum()

        return buy, sell
    except:
        return 0, 0


col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/3310/3310748.png", width=70)

with col_title:
    st.title("CANPOLAT FİNANS")
    durum_ikonu = "🟢" if borsa_acik_mi else "🔴"
    st.caption(f"{durum_ikonu} Piyasa Durumu | Veriler bazı kaynaklarda gecikmeli olabilir")

st.markdown("---")


st.sidebar.markdown("### Ayarlar")
analiz_tipi = st.sidebar.radio("Para Birimi", ["TL (₺)", "Dolar ($)"], horizontal=True)
periyot = st.sidebar.select_slider("Grafik Geçmişi", options=["1mo", "3mo", "1y", "5y"], value="1y")

if st.session_state.favoriler:
    st.sidebar.markdown("### Favoriler")
    fav_sil = st.sidebar.selectbox("Favori Çıkar", ["Seç..."] + st.session_state.favoriler)
    if fav_sil != "Seç...":
        st.session_state.favoriler.remove(fav_sil)
        st.rerun()

st.sidebar.markdown("---")
arama_metni = st.sidebar.text_input("Hisse Ara", placeholder="THY, ASELS vb")

with st.spinner("Veriler çekiliyor..."):
    degisimler = liste_ozeti_getir(HAM_LISTE)

def siralama_anahtari(kod):
    return ISIM_SOZLUGU.get(kod, kod.replace(".IS", ""))

sirali_liste = sorted(HAM_LISTE, key=siralama_anahtari)

st.sidebar.markdown("### CANPOLAT FİNANS")

for kod in sirali_liste:
    ad = ISIM_SOZLUGU.get(kod, kod.replace(".IS", ""))

    if arama_metni:
        if arama_metni.lower() not in ad.lower() and arama_metni.lower() not in kod.lower():
            continue

    yuzde = degisimler.get(kod, 0.0)

    if yuzde > 0:
        badge = "badge-up"
        yuzde_txt = f"%{yuzde:.2f}"
    elif yuzde < 0:
        badge = "badge-down"
        yuzde_txt = f"%{abs(yuzde):.2f}"
    else:
        badge = "badge-flat"
        yuzde_txt = "%0.00"

    aktif_mi = "🟡" if st.session_state.secilen_kod == kod else ""
    fav_ikon = "★" if kod in st.session_state.favoriler else "☆"

    c1, c2, c3 = st.sidebar.columns([0.15, 0.65, 0.2])

    if c1.button(fav_ikon, key=f"fav_{kod}"):
        if kod in st.session_state.favoriler:
            st.session_state.favoriler.remove(kod)
        else:
            st.session_state.favoriler.append(kod)
        st.rerun()

    with c2:
        st.markdown(
            f"""<div style="font-size:13px; font-weight:bold;">{aktif_mi} {ad} <span class="badge {badge}">{yuzde_txt}</span></div>""",
            unsafe_allow_html=True
        )

    if c3.button("➤", key=f"btn_{kod}"):
        st.session_state.secilen_kod = kod
        st.rerun()


secilen_ad = ISIM_SOZLUGU.get(st.session_state.secilen_kod, st.session_state.secilen_kod.replace(".IS", ""))

col_hd_1, col_hd_2 = st.columns([1, 15])

with col_hd_1:
    try:
        if ".IS" in st.session_state.secilen_kod:
            l_url = yf.Ticker(st.session_state.secilen_kod).info.get("logo_url", "")
            if l_url:
                st.image(l_url, width=50)
        elif "GC=F" in st.session_state.secilen_kod:
            st.image("https://cdn-icons-png.flaticon.com/512/10091/10091217.png", width=50)
        elif "SI=F" in st.session_state.secilen_kod:
            st.image("https://cdn-icons-png.flaticon.com/512/10091/10091334.png", width=50)
        elif "USD" in st.session_state.secilen_kod:
            st.image("https://cdn-icons-png.flaticon.com/512/2933/2933884.png", width=50)
    except:
        pass

with col_hd_2:
    st.header(f"{secilen_ad} Analiz Paneli")

tab_grafik, tab_haber, tab_bilgi = st.tabs(["TEKNİK ANALİZ", "PİYASA ÖZETİ", "ŞİRKET KARTI"])


with tab_grafik:
    df = detay_veri(st.session_state.secilen_kod, analiz_tipi, periyot)

    if not df.empty and "Close" in df.columns and len(df) > 20:
        df["SMA20"] = df["Close"].rolling(window=20).mean()
        df["SMA50"] = df["Close"].rolling(window=50).mean()
        df["RSI"] = calculate_rsi(df["Close"])

        son = df["Close"].iloc[-1]
        onceki = df["Close"].iloc[-2] if len(df["Close"]) > 1 else son
        degisim_val = ((son - onceki) / onceki) * 100 if onceki != 0 else 0
        simge = "₺" if analiz_tipi == "TL (₺)" else "$"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fiyat", f"{son:.2f} {simge}", f"%{degisim_val:.2f}")
        m2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
        m3.metric("SMA 20", f"{df['SMA20'].iloc[-1]:.2f}")
        m4.metric("Hacim", f"{df['Volume'].iloc[-1] / 1000000:.1f}M")

        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            row_width=[0.2, 0.2, 0.6],
            vertical_spacing=0.03
        )

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Fiyat"
        ), row=1, col=1)

        fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", row=2, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Hacim"), row=3, col=1)

        fig.update_layout(
            template="plotly_dark",
            height=700,
            xaxis_rangeslider_visible=False,
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Gün İçi Hacim Analizi")

        alis, satis = hesapla_hacim_analizi(st.session_state.secilen_kod)

        if alis + satis > 0:
            top = alis + satis
            a_yuz = (alis / top) * 100
            s_yuz = (satis / top) * 100

            st.markdown(f"""
            <div class="depth-container">
                <div class="depth-buy" style="width: {a_yuz}%;">ALIŞ %{a_yuz:.0f}</div>
                <div class="depth-sell" style="width: {s_yuz}%;">SATIŞ %{s_yuz:.0f}</div>
            </div>
            """, unsafe_allow_html=True)

            st.caption("Bu veri gerçekleşen hacim yönüdür, derinlik verisi değildir")
        else:
            st.info("Yeterli hacim verisi yok")
    else:
        st.error("Veri bulunamadı")


with tab_haber:
    st.subheader(f"{secilen_ad} Haber ve Özet")

    haberler = google_rss_haberleri(f"{secilen_ad} hisse")

    if haberler:
        basliklar_listesi = [h["title"] for h in haberler]

        if AI_AKTIF:
            with st.spinner("AI özet hazırlıyor..."):
                ozet_metni = gemini_piyasa_ozeti(basliklar_listesi, secilen_ad)
                st.info(ozet_metni)
        else:
            st.warning("AI kapalı veya anahtar yok")

        st.markdown("---")
        st.markdown("Haberler")
        for h in haberler:
            st.write(f"🔗 [{h['title']}]({h['link']}) - *{h['pubDate']}*")
    else:
        st.info("Haber bulunamadı")


with tab_bilgi:
    try:
        if ".IS" in st.session_state.secilen_kod:
            tik = yf.Ticker(st.session_state.secilen_kod)
            info = tik.info

            st.write(f"**Sektör:** {info.get('sector', '-')}")
            st.write(info.get("longBusinessSummary", "Bilgi yok"))
        else:
            st.info("Şirket bilgisi yok")
    except:
        st.write("Bilgi alınamadı")