import argparse
from .data.market import synthetic_symbol
from .features.build import make_features
from .models.walk_forward import walk_forward
from .backtest.engine import backtest_oos
from .data.ingest_pipeline import run_real_ingestion, assert_point_in_time_integrity
from .data.pit_builder import build_pit_dataset
from .data.pit_validator import validate_pit_dataset
from .data.reporting import generate_all_reports

def main():
    p=argparse.ArgumentParser(description='NSE Signal Provider research CLI')
    p.add_argument('--sample', action='store_true')
    p.add_argument('--rows', type=int, default=360)
    p.add_argument('--ingest', action='store_true')
    p.add_argument('--bootstrap', action='store_true')
    p.add_argument('--audit', action='store_true')
    p.add_argument('--build-pit', action='store_true')
    p.add_argument('--validate-pit', action='store_true')
    p.add_argument('--start-date', type=str, default="2025-01-02")
    p.add_argument('--end-date', type=str, default="2025-01-02")
    args=p.parse_args()

    if args.sample:
        df=make_features(synthetic_symbol(n=args.rows))
        oos=walk_forward(df)
        _, stats=backtest_oos(oos.predictions)
        print('OOS METRICS:', oos.metrics)
        print('BACKTEST:', stats)
        return

    executed = False
    if args.ingest or args.bootstrap:
        print(f"Executing Real NSE Ingestion from {args.start_date} to {args.end_date}...")
        summary = run_real_ingestion(args.start_date, args.end_date)
        print(f"Ingestion complete. Successful trading dates: {len(summary.get('successful_trading_dates', []))}/{len(summary.get('expected_trading_dates', []))}")
        executed = True

    if args.audit:
        print("Executing Data Audit & Report Generation...")
        r1, r2, r3, r4, r5 = generate_all_reports()
        print(f"Audit reports generated: {r1}, {r2}, {r3}, {r4}, {r5}")
        executed = True

    if args.build_pit:
        print("Executing PIT Dataset Builder...")
        pit_res = build_pit_dataset()
        print(f"PIT Build complete. Status: {pit_res.get('status')}, Canonical Records: {pit_res.get('canonical_rows')}")
        executed = True

    if args.validate_pit:
        print("Executing PIT Dataset Validator...")
        val_res = validate_pit_dataset()
        print(f"PIT Validation complete. Status: {val_res.get('validation_status')}, Passed: {val_res.get('checks_passed')}")
        executed = True

    if executed:
        assert_point_in_time_integrity("2025-01-02T15:30:00Z", "RELIANCE")
        print("V31 Pipeline execution pipeline stages finished successfully.")
        return

    p.print_help()

if __name__ == '__main__': main()
