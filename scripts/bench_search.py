"""Benchmark linear, binary, and dictionary SKU search on 1k, 10k, and 100k items."""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from tiendita.search import ProductRecord, binary_search, build_sku_index, dict_search, linear_search


def run_benchmark() -> None:
    print(f"{'N':>8} | {'Linear (ops / ms)':>22} | {'Binary (ops / ms)':>22} | {'Dict (ops / ms)':>20}")
    print("-" * 82)
    for size in (1_000, 10_000, 100_000):
        products = [
            ProductRecord(sku=f"SKU-{i:06d}", name=f"Item {i}", category="general", price_cents=1000, stock=5)
            for i in range(size)
        ]
        target = f"SKU-{size - 1:06d}"
        index = build_sku_index(products)

        t0 = time.perf_counter()
        lin = linear_search(products, target)
        t_lin = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        bin_r = binary_search(products, target)
        t_bin = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        dic = dict_search(index, target)
        t_dic = (time.perf_counter() - t0) * 1000

        print(
            f"{size:>8} | {lin.operations:>8} / {t_lin:>8.3f} ms | "
            f"{bin_r.operations:>8} / {t_bin:>8.3f} ms | {dic.operations:>6} / {t_dic:>8.3f} ms"
        )


if __name__ == "__main__":
    run_benchmark()
