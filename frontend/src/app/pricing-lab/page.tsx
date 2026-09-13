import { SectionPlaceholder } from "@/components/section-placeholder";
export default function PricingLab() {
  return <SectionPlaceholder title="Pricing Lab"
    description="Learn dividend-adjusted European Black–Scholes pricing and Delta, Gamma, Vega, and Theta."
    limitation="The pricing model is not implemented yet. It will use a continuous dividend yield, decimal rates and volatility, and time in years. European pricing does not capture early exercise in American-style contracts. Market quotes and theoretical prices will have distinct labels." />;
}
