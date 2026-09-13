import { SectionPlaceholder } from "@/components/section-placeholder";
export default function OptionChain() {
  return <SectionPlaceholder title="Option Chain"
    description="Explore normalized option quotes by expiry and strike, with visible quote-quality flags."
    limitation="No market-data provider is connected. Bid, ask, last trade, timestamps, and quote validity will be shown when real option-chain integration is implemented." />;
}
