from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine( # veritabanina fiziksel baglanti saglayan engine nesnesi olusturuyor
    settings.DATABASE_URL, #baglanilacak veri tabani url
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
    #eger sqlite kullaniliyorsa check_same_thread=false ayari eklenir
    #bu ayar sqlite tek thread sinirini devre disi birakir
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# veritabani oturumunu olusturmak icin bir session maker uretilir
#bind=engine bu session yukaridaki engine uzerinden calisir
#autoflush=False her islemden sonra otomatik flush yani degisiklikleri veritabanina yansitma yapilmaz
#autocommit islemler otomatik commit edilmez