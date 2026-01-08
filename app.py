import math
from flask import Flask, render_template, request

app = Flask(__name__)

# -----------------------------
# Queueing M/M/2 (Erlang-C) - SAMA PERSIS DENGAN KODE ANDA
# -----------------------------
def mmc_erlang_c(interarrival_min: float, service_min: float, c: int = 2):
    """
    Menghitung metrik antrian M/M/c dengan rumus Erlang-C.
    Semua satuan waktu dalam MENIT.
    """
    lam = 1.0 / interarrival_min       # λ (customers per minute)
    mu = 1.0 / service_min             # μ (customers per minute per server)
    rho = lam / (c * mu)               # utilization

    if rho >= 1.0:
        raise ValueError("Sistem tidak stabil karena ρ ≥ 1. Kurangi kedatangan atau percepat pelayanan.")

    a = lam / mu  # offered load

    # P0
    sum_terms = sum((a ** n) / math.factorial(n) for n in range(c))
    last_term = (a ** c) / math.factorial(c) * (1.0 / (1.0 - rho))
    P0 = 1.0 / (sum_terms + last_term)

    # Erlang-C: probability an arrival must wait (Pw)
    Pw = last_term * P0

    # Lq, Wq, W
    Lq = P0 * ((a ** c) * rho) / (math.factorial(c) * ((1.0 - rho) ** 2))
    Wq = Lq / lam
    W = Wq + (1.0 / mu)

    return {
        "lambda": lam,
        "mu": mu,
        "c": c,
        "rho": rho,
        "a": a,
        "P0": P0,
        "Pw": Pw,
        "Lq": Lq,
        "Wq": Wq,
        "W": W,
        "L": lam * W,
        # helper untuk step-by-step
        "sum_terms": sum_terms,
        "last_term": last_term,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    # default sesuai soal
    interarrival = 4.0
    service_time = 3.0
    c = 2  # karena M/M/2 dan select di HTML disabled (tidak terkirim)

    error = None
    res = None
    active_tab = "perhitungan"  # default: langsung tampil step-by-step

    if request.method == "POST":
        try:
            interarrival_raw = request.form.get("interarrival", "").strip()
            service_raw = request.form.get("service_time", "").strip()

            # ambil tab dari hidden input (agar setelah submit tetap di tab yang dipilih)
            active_tab = request.form.get("tab", "perhitungan").strip() or "perhitungan"

            # validasi kosong
            if not interarrival_raw or not service_raw:
                raise ValueError("Input tidak boleh kosong.")

            interarrival = float(interarrival_raw)
            service_time = float(service_raw)

            # validasi positif
            if interarrival <= 0 or service_time <= 0:
                raise ValueError("Input harus bernilai positif (> 0).")

            res = mmc_erlang_c(interarrival, service_time, c=c)

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        interarrival=interarrival,
        service_time=service_time,
        c=c,
        error=error,
        res=res,
        active_tab=active_tab,   # <-- PENTING: dipakai di HTML/JS
    )


if __name__ == "__main__":
    app.run(debug=True)
