# test.py

from app.predict.ada_model import predict_ada_next_day
from app.predict.bnb_model import predict_bnb_next_day
from app.predict.btc_model import predict_next_day as predict_btc_next_day
from app.predict.doge_model import predict_doge_next_day
from app.predict.eth_model import predict_eth_next_day
from app.predict.sol_model import predict_sol_next_day
from app.predict.trx_model import predict_trx_next_day
from app.predict.xrp_model import predict_xrp_next_day

from app.log_config import logger


def run_all_predictions():
    logger.info("🔄 Tüm coinler için tahminler başlatılıyor...")

    try:
        predict_btc_next_day()
        logger.info("✅ BTC tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ BTC tahmini hatası: {e}")

    try:
        predict_eth_next_day()
        logger.info("✅ ETH tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ ETH tahmini hatası: {e}")

    try:
        predict_ada_next_day()
        logger.info("✅ ADA tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ ADA tahmini hatası: {e}")

    try:
        predict_bnb_next_day()
        logger.info("✅ BNB tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ BNB tahmini hatası: {e}")

    try:
        predict_xrp_next_day()
        logger.info("✅ XRP tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ XRP tahmini hatası: {e}")

    try:
        predict_doge_next_day()
        logger.info("✅ DOGE tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ DOGE tahmini hatası: {e}")

    try:
        predict_sol_next_day()
        logger.info("✅ SOL tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ SOL tahmini hatası: {e}")

    try:
        predict_trx_next_day()
        logger.info("✅ TRX tahmini tamamlandı.")
    except Exception as e:
        logger.error(f"⛔ TRX tahmini hatası: {e}")

    logger.info("✅ Tüm tahminler başarıyla tamamlandı.")


if __name__ == "__main__":
    run_all_predictions()
