# The Living Dot
A single dot that evolves on its own. A GitHub Action runs `evolve.py` every 30 minutes: it mutates the dot's genes
(speed, sense, turn, metabolism, colour), keeps whatever survives better in a simulated world, and also adapts its own
mutation size. Milestones become portfolio entries on the page. The dot only ever edits JSON data, never code.

## Start it
1. Push all these files to a new GitHub repo (keep the `.github` folder).
2. Settings > Pages > deploy from branch `main`, folder `/ (root)`.
3. Actions tab > "evolve" > Run workflow (the schedule takes over after that).
4. Optional: add a repo secret `ANTHROPIC_API_KEY` so Claude writes the portfolio blurbs.
To preview locally: `python -m http.server`, then open http://localhost:8000
