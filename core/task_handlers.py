"""Deterministic local-only handlers for catalog tasks; no external side effects."""
from __future__ import annotations
import math, re
from collections import Counter, defaultdict
from datetime import datetime

def _minor(p, k, default=None):
    v=p.get(k,default)
    if not isinstance(v,int) or isinstance(v,bool) or v<0: raise ValueError(f"{k} must be a non-negative integer")
    return v

def _currency(p):
    v=p.get("currency")
    if not isinstance(v,str) or not re.fullmatch(r"[A-Za-z]{3}",v): raise ValueError("currency must be a three-letter code")
    return v.upper()

def _num(v,k,lo=None,hi=None):
    if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v): raise ValueError(f"{k} must be finite")
    if (lo is not None and v<lo) or (hi is not None and v>hi): raise ValueError(f"{k} outside permitted bounds")
    return float(v)

def _ts(v):
    try:
        datetime.fromisoformat(v.strip().replace("Z","+00:00"))
        return isinstance(v,str) and bool(v.strip())
    except (ValueError,AttributeError):
        return False

def _record_sources(t,s):
    refs=t.payload.get("source_refs")
    if not isinstance(refs,list) or not refs: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"source_refs_required"}
    if len(refs)>50: return {"task_id":t.task_id,"state":"BLOCKED","reason":"too_many_sources"}
    clean=[]
    for x in refs:
        if not isinstance(x,dict) or not isinstance(x.get("url"),str) or not x["url"].startswith("https://") or not isinstance(x.get("provider_id"),str) or not x["provider_id"].strip() or not _ts(x.get("observed_at")):
            return {"task_id":t.task_id,"state":"BLOCKED","reason":"source_reference_invalid"}
        clean.append({"url":x["url"],"provider_id":x["provider_id"][:120],"observed_at":x["observed_at"]})
    return {"task_id":t.task_id,"state":"SUCCEEDED","result":{"status":"STRUCTURE_VALIDATED","sources":clean,"remote_fetch_performed":False,"license_verified":False}}

def _score_opportunity(t,s):
    records,evidence=t.payload.get("validated_records"),t.payload.get("evidence")
    if not isinstance(records,list) or not records or not isinstance(evidence,list) or not evidence:
        return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"validated_records_and_evidence_required"}
    if len(records)>100: return {"task_id":t.task_id,"state":"BLOCKED","reason":"too_many_records"}
    out=[]
    keys=("demand_score","evidence_score","unit_economics_score","risk_score")
    for i,row in enumerate(records):
        if not isinstance(row,dict): return {"task_id":t.task_id,"state":"BLOCKED","reason":"record_must_be_object"}
        vals=[row.get(k) for k in keys]
        if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or not 0<=v<=100 for v in vals):
            return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"explicit_component_scores_required"}
        d,e,u,r=vals
        out.append({"record_id":str(row.get("record_id",i))[:100],"score":round(.30*d+.25*e+.25*u+.20*(100-r),2)})
    out.sort(key=lambda x:x["score"],reverse=True)
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"status":"RANKED_FROM_SUPPLIED_SCORES","formula_version":"1.0","formula":"0.30*demand + 0.25*evidence + 0.25*unit_economics + 0.20*(100-risk)","records":out,"evidence_count":len(evidence),"external_sources_verified":False,"revenue_confirmed":False}}

def _identify_customer_pain(t,s):
    rows=t.payload.get("validated_records")
    if not isinstance(rows,list) or not rows: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"validated_records_required"}
    counts,refs=Counter(),defaultdict(list)
    for row in rows:
        if not isinstance(row,dict): continue
        for pain in row.get("pain_points",[]) if isinstance(row.get("pain_points"),list) else []:
            if isinstance(pain,str) and pain.strip():
                key=pain.strip()[:160]; counts[key]+=1
                if isinstance(row.get("evidence_ref"),str): refs[key].append(row["evidence_ref"][:200])
    if not counts: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"pain_points_required"}
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"status":"AGGREGATED_FROM_SUPPLIED_RECORDS","pain_points":[{"pain_point":k,"mentions":n,"evidence_refs":sorted(set(refs[k]))} for k,n in counts.most_common(30)],"source_records":len(rows),"market_representativeness_verified":False}}

def _compare_commissions(t,s):
    programs=t.payload.get("programs")
    if not isinstance(programs,list) or not programs: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"program_terms_required"}
    out=[]
    for p in programs:
        if not isinstance(p,dict): return {"task_id":t.task_id,"state":"BLOCKED","reason":"program_must_be_object"}
        rate=_num(p.get("commission_bps"),"commission_bps",0,10000)
        reversal=_num(p.get("reversal_bps",0),"reversal_bps",0,10000)
        cookie=_num(p.get("cookie_days"),"cookie_days",0,3650)
        out.append({"program_id":str(p.get("program_id",""))[:100],"effective_commission_bps":round(rate*(10000-reversal)/10000,2),"cookie_days":int(cookie),"payout_threshold_minor":_minor(p,"payout_threshold_minor",0),"currency":_currency(p),"terms_verified":False})
    out.sort(key=lambda x:x["effective_commission_bps"],reverse=True)
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"programs":out,"provider_terms_fetched":False,"eligibility_verified":False}}

def _calculate_total_price(t,s):
    p=t.payload
    if "product_minor" not in p: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"product_minor_required"}
    product=_minor(p,"product_minor"); shipping=_minor(p,"shipping_minor",0); tax=_minor(p,"tax_minor",0); fees=_minor(p,"fees_minor",0)
    return {"task_id":t.task_id,"state":"SUCCEEDED","result":{"currency":_currency(p),"product_minor":product,"shipping_minor":shipping,"tax_minor":tax,"fees_minor":fees,"total_minor":product+shipping+tax+fees,"checkout_created":False}}

def _normalize_catalog(t,s):
    items=t.payload.get("items")
    if not isinstance(items,list) or not items: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"catalog_items_required"}
    out=[]
    for x in items:
        if not isinstance(x,dict) or not isinstance(x.get("sku"),str) or not x["sku"].strip(): return {"task_id":t.task_id,"state":"BLOCKED","reason":"sku_required"}
        cat=x.get("category","")
        if not isinstance(cat,str) or not isinstance(x.get("variants",[]),list): return {"task_id":t.task_id,"state":"BLOCKED","reason":"catalog_field_invalid"}
        out.append({"sku":x["sku"].strip().upper(),"category":re.sub(r"[^a-z0-9]+","-",cat.lower()).strip("-"),"variants":x.get("variants",[]),"external_catalog_modified":False})
    return {"task_id":t.task_id,"state":"SUCCEEDED","result":{"items":out,"normalized_count":len(out)}}

def _deduplicate_catalog(t,s):
    items=t.payload.get("items")
    if not isinstance(items,list) or not items: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"catalog_items_required"}
    groups=defaultdict(list)
    for i,x in enumerate(items):
        if not isinstance(x,dict) or not isinstance(x.get("sku"),str) or not x["sku"].strip(): return {"task_id":t.task_id,"state":"BLOCKED","reason":"sku_required"}
        groups[x["sku"].strip().upper()].append(i)
    dup=[{"sku":k,"indices":v} for k,v in groups.items() if len(v)>1]
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW" if dup else "SUCCEEDED","result":{"duplicate_groups":dup,"duplicate_count":sum(len(x["indices"])-1 for x in dup),"records_deleted":False}}

def _verify_price_stock(t,s):
    items=t.payload.get("items")
    if not isinstance(items,list) or not items: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"catalog_items_required"}
    out=[]
    for x in items:
        if not isinstance(x,dict): return {"task_id":t.task_id,"state":"BLOCKED","reason":"catalog_item_invalid"}
        price=_minor(x,"price_minor"); stock=x.get("stock")
        if not isinstance(stock,int) or isinstance(stock,bool) or stock<0: return {"task_id":t.task_id,"state":"BLOCKED","reason":"stock_invalid"}
        out.append({"sku":str(x.get("sku",""))[:100],"price_minor":price,"stock":stock,"currency":_currency(x),"timestamp_parseable":_ts(x.get("observed_at")),"freshness_verified":False})
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"items":out,"external_price_stock_verified":False}}

def _configure_margin(t,s):
    p=t.payload
    missing=[k for k in ("product_cost_minor","sale_price_minor","commission_bps") if k not in p]
    if missing: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"unit_economics_inputs_required","missing_required_inputs":missing}
    cost=_minor(p,"product_cost_minor"); sale=_minor(p,"sale_price_minor"); rate=int(_num(p["commission_bps"],"commission_bps",0,10000))
    commission=(sale*rate+5000)//10000
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"currency":_currency(p),"product_cost_minor":cost,"sale_price_minor":sale,"commission_bps":rate,"commission_minor":commission,"gross_margin_minor":sale-cost,"net_contribution_before_tax_minor":sale-cost-commission,"price_rule_published":False}}

def _net_after_reserves(t,s):
    p=t.payload; fields=("confirmed_cash_minor","vat_reserved_minor","tax_reserved_minor","fees_minor","refunds_reserved_minor","committed_costs_minor","emergency_reserve_minor")
    missing=[k for k in fields if k not in p]
    if missing: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"cash_and_reserve_inputs_required","missing_required_inputs":missing}
    values={k:_minor(p,k) for k in fields}; pending=_minor(p,"pending_cash_minor",0)
    net=values["confirmed_cash_minor"]-sum(v for k,v in values.items() if k!="confirmed_cash_minor")
    state="HUMAN_REVIEW" if t.task_key=="calculate_potential_available_capital" else "SUCCEEDED"
    return {"task_id":t.task_id,"state":state,"result":{"currency":_currency(p),**values,"pending_cash_excluded_minor":pending,"net_after_obligations_minor":net,"potential_available_minor":max(0,net),"shortfall_minor":max(0,-net),"uses_only_confirmed_cash":True,"status":"PROPOSAL_REQUIRES_OWNER_REVIEW" if state=="HUMAN_REVIEW" else "INTERNAL_CALCULATION","investment_order_allowed":False}}

def _separate_cash(t,s):
    p=t.payload
    if "confirmed_cash_minor" not in p or "pending_cash_minor" not in p: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"cash_inputs_required"}
    return {"task_id":t.task_id,"state":"SUCCEEDED","result":{"currency":_currency(p),"confirmed_cash_minor":_minor(p,"confirmed_cash_minor"),"pending_cash_minor":_minor(p,"pending_cash_minor"),"pending_is_available_cash":False}}

def _identify_instrument(t,s):
    p=t.payload; allowed={"equity","etf","bond","fund","gold","commodity"}
    if p.get("asset_class") not in allowed: return {"task_id":t.task_id,"state":"BLOCKED","reason":"asset_class_not_permitted_or_not_recognized"}
    missing=[k for k in ("instrument_id","issuer","market","currency") if not p.get(k)]
    if missing: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"instrument_identity_incomplete","missing_required_inputs":missing}
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"instrument_id":str(p["instrument_id"])[:100],"issuer":str(p["issuer"])[:160],"market":str(p["market"])[:100],"asset_class":p["asset_class"],"currency":_currency(p),"identity_verified_with_primary_source":False,"order_allowed":False}}

def _assess_risks(t,s):
    p=t.payload; fields=("issuer_concentration_pct","liquidity_days","fx_exposure_pct","max_issuer_concentration_pct","max_liquidity_days","max_fx_exposure_pct")
    missing=[k for k in fields if k not in p]
    if missing: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"explicit_risk_inputs_and_limits_required","missing_required_inputs":missing}
    c=_num(p["issuer_concentration_pct"],"issuer_concentration_pct",0,100); l=_num(p["liquidity_days"],"liquidity_days",0); f=_num(p["fx_exposure_pct"],"fx_exposure_pct",0,100)
    mc=_num(p["max_issuer_concentration_pct"],"max_issuer_concentration_pct",0,100); ml=_num(p["max_liquidity_days"],"max_liquidity_days",0); mf=_num(p["max_fx_exposure_pct"],"max_fx_exposure_pct",0,100)
    flags=[]
    if c>mc: flags.append("issuer_concentration")
    if l>ml: flags.append("liquidity")
    if f>mf: flags.append("fx_exposure")
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"risk_flags":flags,"within_supplied_limits":not flags,"limits_are_owner_supplied":True,"investment_order_allowed":False}}

def _build_scenarios(t,s):
    p=t.payload; fields=("reference_price_minor","adverse_change_bps","base_change_bps","favorable_change_bps")
    missing=[k for k in fields if k not in p]
    if missing: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"scenario_inputs_required","missing_required_inputs":missing}
    ref=_minor(p,"reference_price_minor"); a=int(_num(p["adverse_change_bps"],"adverse_change_bps",-10000,100000)); b=int(_num(p["base_change_bps"],"base_change_bps",-10000,100000)); f=int(_num(p["favorable_change_bps"],"favorable_change_bps",-10000,100000))
    if not a<=b<=f: return {"task_id":t.task_id,"state":"BLOCKED","reason":"scenario_order_invalid"}
    calc=lambda x:(ref*(10000+x)+5000)//10000
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"currency":_currency(p),"scenarios_minor":{"adverse":calc(a),"base":calc(b),"favorable":calc(f)},"scenario_inputs_supplied":True,"forecast_or_prediction":False}}

def _record_price_context(t,s):
    p=t.payload; fields=("price_minor","bid_minor","ask_minor","volume","fee_bps","observed_at")
    missing=[k for k in fields if k not in p]
    if missing: return {"task_id":t.task_id,"state":"NEEDS_ADAPTER","reason":"price_context_inputs_required","missing_required_inputs":missing}
    price,bid,ask=(_minor(p,k) for k in ("price_minor","bid_minor","ask_minor"))
    volume=_num(p["volume"],"volume",0); fees=_num(p["fee_bps"],"fee_bps",0)
    if bid>ask or not bid<=price<=ask: return {"task_id":t.task_id,"state":"BLOCKED","reason":"bid_ask_price_inconsistent"}
    if not _ts(p["observed_at"]): return {"task_id":t.task_id,"state":"BLOCKED","reason":"timestamp_invalid"}
    mid=(bid+ask)/2; spread=round((ask-bid)/mid*10000,2) if mid else 0
    return {"task_id":t.task_id,"state":"HUMAN_REVIEW","result":{"price_minor":price,"bid_minor":bid,"ask_minor":ask,"spread_bps":spread,"volume":volume,"fee_bps":fees,"currency":_currency(p),"freshness_verified":False,"source_verified":False}}

class _Handler:
    def __init__(self, fn): self.fn=fn
    def run(self, task, spec): return self.fn(task,spec)

def build_task_handlers():
    funcs={
      ("ALPHA","market_intelligence","record_sources"):_record_sources,
      ("ALPHA","market_intelligence","score_opportunity"):_score_opportunity,
      ("ALPHA","market_intelligence","identify_customer_pain"):_identify_customer_pain,
      ("ALPHA","affiliate_operations","compare_commissions"):_compare_commissions,
      ("BETA","merchandising","calculate_total_price"):_calculate_total_price,
      ("BETA","treasury_controls","calculate_net_after_reserves"):_net_after_reserves,
      ("BETA","seller_catalog","normalize_skus_variants_categories"):_normalize_catalog,
      ("BETA","seller_catalog","deduplicate_catalog"):_deduplicate_catalog,
      ("BETA","seller_catalog","verify_price_stock_currency_timestamp"):_verify_price_stock,
      ("BETA","merchandising","configure_margin_commission_rules"):_configure_margin,
      ("GAMMA","capital_reserves","separate_confirmed_and_pending_cash"):_separate_cash,
      ("GAMMA","capital_reserves","calculate_potential_available_capital"):_net_after_reserves,
      ("GAMMA","research_analysis","identify_exact_instrument"):_identify_instrument,
      ("GAMMA","research_analysis","assess_market_issuer_concentration_liquidity_fx_risks"):_assess_risks,
      ("GAMMA","research_analysis","build_adverse_base_favorable_scenarios"):_build_scenarios,
      ("GAMMA","research_analysis","record_price_currency_liquidity_spread_fees"):_record_price_context,
    }
    return {key:_Handler(fn) for key,fn in funcs.items()}
