"""The Dot's evolution engine. Mutates genes, keeps what survives better, records milestones.
Safety boundary: it only edits JSON data. It never executes generated code."""
import json, random, math, os, datetime, urllib.request
now = lambda: datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"
rd = lambda p, d: json.load(open(p)) if os.path.exists(p) else d
wr = lambda p, d: json.dump(d, open(p, "w"), indent=1)
LIM = {"speed": (.5, 6), "sense": (5, 120), "turn": (.02, .6), "metab": (.2, 2), "hue": (0, 360)}
MILES = [  # (fitness needed, title, text, skill tags)
 (3, "First meal", "Evolved a foraging loop that finds and eats food.", ["Simulation"]),
 (10, "Efficient forager", "Balanced speed and sensing to waste less energy.", ["Evolutionary algorithms", "Optimisation"]),
 (20, "Self-tuning mutation", "Mutation size adapts to its own progress.", ["Self-adaptive systems"]),
 (35, "Unattended pipeline", "Keeps evolving on a schedule with no human involved.", ["GitHub Actions", "Automation"]),
 (50, "Expert forager", "Reached expert-level survival in its simulated world.", ["AI engineering"])]

def sim(g, seed, steps=600, n=30, S=300):
    r = random.Random(seed); f = [[r.uniform(0, S), r.uniform(0, S)] for _ in range(n)]
    x = y = S / 2; a = 0; e = 40; eaten = 0
    for t in range(steps):
        d, b = min(((math.hypot(p[0] - x, p[1] - y), p) for p in f), key=lambda q: q[0])
        if d < g["sense"]:
            df = (math.atan2(b[1] - y, b[0] - x) - a + math.pi) % (2 * math.pi) - math.pi
            a += max(-g["turn"], min(g["turn"], df))
        else:
            a += r.uniform(-g["turn"], g["turn"])
        x = (x + math.cos(a) * g["speed"]) % S; y = (y + math.sin(a) * g["speed"]) % S
        e -= .05 * g["metab"] + .02 * g["speed"] ** 2 + .002 * g["sense"]  # acting costs energy
        if d < 5: eaten += 1; e += 8; b[0], b[1] = r.uniform(0, S), r.uniform(0, S)
        if e <= 0: break
    return eaten + t / steps

def mutate(g, s, r):
    return {k: min(hi, max(lo, g[k] + r.gauss(0, s * (hi - lo) * .2))) for k, (lo, hi) in LIM.items()}

def blurb(m, gm):  # optional: Claude words the portfolio entry (text only)
    k = os.getenv("ANTHROPIC_API_KEY")
    if not k: return m[2]
    try:
        body = {"model": os.getenv("MODEL", "claude-sonnet-5-5"), "max_tokens": 120, "messages": [{"role": "user",
                "content": f"Write 2 plain sentences for an AI developer portfolio about this milestone of an evolving simulation: {m[1]} (generation {gm['gen']}, fitness {gm['fitness']}, genes {gm['genes']}). No hype."}]}
        q = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
            {"x-api-key": k, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        return json.load(urllib.request.urlopen(q, timeout=30))["content"][0]["text"].strip()
    except Exception:
        return m[2]

def main():
    gm = rd("genome.json", None); H = rd("history.json", []); P = rd("portfolio.json", []); r = random.Random()
    for _ in range(int(os.getenv("GENS", 5))):
        seeds = [r.randrange(10 ** 9) for _ in range(6)]
        fit = lambda g: sum(sim(g, s) for s in seeds) / len(seeds)
        base = fit(gm["genes"]); best, bf = gm["genes"], base
        for _ in range(20):
            c = mutate(gm["genes"], gm["sigma"], r); cf = fit(c)
            if cf > bf: best, bf = c, cf
        # the dot also evolves HOW it evolves: bigger steps after success, smaller after failure
        gm["sigma"] = round(min(.5, max(.02, gm["sigma"] * (1.1 if bf > base else .92))), 4)
        gm["genes"] = {k: round(v, 3) for k, v in best.items()}; gm["gen"] += 1; gm["fitness"] = round(bf, 2)
        H.append({"gen": gm["gen"], "fitness": gm["fitness"]})
        for m in MILES:
            if bf >= m[0] and not any(p["title"] == m[1] for p in P):
                P.append({"title": m[1], "text": blurb(m, gm), "tags": m[3], "gen": gm["gen"], "date": now()})
    wr("genome.json", gm); wr("history.json", H[-5000:]); wr("portfolio.json", P)
    print("generation", gm["gen"], "fitness", gm["fitness"])

if __name__ == "__main__": main()
