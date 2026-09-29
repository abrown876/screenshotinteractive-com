# The Bigger Picture: editorial guide

The Bigger Picture is Screenshot Interactive's industry news series, published on screenshotinteractive.com/the-bigger-picture and on Instagram @screenshotja. Every story is drafted for Andrew Brown's approval before it is published. This guide is the standing brief for anyone (or any automated run) writing a draft.

## 1. What we cover, in priority order

1. **Jamaica and the Caribbean.** Local marketing, media, events, sponsorship, creators, tourism marketing, retail and brand news. This is the default. At least one story every week comes from here.
2. **The diaspora.** Jamaican and Caribbean audiences in the US, UK and Canada, and how brands reach them. About twice a month.
3. **Major global industry news.** Platform changes, big industry forecasts, landmark campaigns. Only when it genuinely matters to a Jamaican marketer, and always with a section on what it means here. At most one a week.
4. **Creator Spotlights.** Stories about creators on the Screenshot roster (see section 5). About twice a month.

Each story must connect to at least one thing Screenshot does:
- Brand activations and the Mobile Magic Mirror → `/activations`, `/activations/magic-mirror`
- Creator Network → `/creators`
- Digital billboard at Chilitos, Hope Road → `/activations/digital-advertising`
- Social Cine' → `/social-cine`
- Screen Test live trivia → `/screen-test`

## 2. Write original stories, not summaries

- **Find our own angle.** Ask: what does this mean for a brand, venue or marketer in Jamaica? Lead with that, not with who published the report.
- **Our headline, our structure.** Never mirror a source's headline, order or section headers.
- **Sources are reporting inputs.** Weave attribution in naturally ("Bank of Jamaica figures show…", "told the Jamaica Observer…"). Do not open with "According to a new report…".
- **Quotes:** at most one short quote per source, under 15 words, only when the exact words matter. Paraphrase everything else fully in our own words.
- **Combine.** The best stories connect two or three sources, for example a local event plus a global trend, or official figures plus what a practitioner said.
- **Voice:** direct, confident, Jamaican-market literate. Short sentences. No hype words ("game-changer", "revolutionary"), no press-release tone, no filler.

## 3. Accuracy rules

- Every number, quote and claim must trace to a source listed at the bottom of the story.
- Check the date of every statistic. Anything more than two years old is history, not news. Say the year, or leave it out. (Example: the widely quoted "98% of event guests create content" figure is from 2015.)
- Say exactly what the source says. Do not upgrade a forecast to a fact, a US figure to a Caribbean one, or one person's view to an industry consensus.
- Label forecasts as forecasts and name who made them.
- If a source reads like promotion (no names, no dates, no numbers), do not use it.
- Never use photos from news outlets or other brands. Use only the photo library (`assets/bigger-picture/library/library.json`) or a text card.

## 4. Things we do not publish

- Client work, rates or campaign details unless the client has approved it and it is already public.
- Anything about RJRGLEANER's commercial dealings, including billboard partnership discussions.
- Party politics, crime or tragedy, except where a story is plainly about the marketing industry (for example, tourism marketing after a hurricane) and handled with care.
- Negative stories about named competitors.
- Photos of guests at private events (weddings, birthdays). Client-branded event photos only with the client's OK (`clientBranded: true` in the library).

## 5. Creator Spotlights

Current roster (keep in sync with `/creators`): Simon Tomlinson (TomoTV), Toni-Ann Bedassie, Trisan Bent (Trisanze Trizzy), Justin Whitelocke (JustInJA), Kellandra.

- **Purpose:** show brands who the creator is, who their audience is and what their content does well. Celebrate the creator; do not sell hard.
- **What to use:** their public content and profile, their published roster stats, public appearances and press coverage. Stats must match the `/creators` page.
- **What not to use:** brand campaigns in progress, fees, contracts or anything from private correspondence.
- **Approval:** every Spotlight needs the creator's OK before publishing. Mark the draft `"needsCreatorOK": true` and name the creator in the approval note.
- **End with:** how brands can work with them (Creator Network page and talent@screenshotinteractive.com).

## 6. Story format

- 350 to 600 words.
- Headline: 4 to 12 words, specific, no clickbait.
- Dek: one sentence saying why it matters.
- Body: 3 to 6 short paragraphs, plus at most two subheads and one list.
- **"The takeaway":** one or two sentences a reader can act on.
- **"How Screenshot can help":** one link to the matching service.
- Sources: every source, with publisher and date.

## 7. Instagram caption

- 2 to 4 short lines saying what happened and why it matters here.
- "Full story: link in bio."
- Source credit: "Source: [publisher]".
- 3 to 6 hashtags, always including #TheBiggerPicture.
- For Spotlights, tag the creator's handle.

## 8. Cards

- **Cover card:** a library photo fills the frame, with type on a dark fade. Use it when a library photo genuinely fits the story.
- **Bold Navy card:** text only. Use it for stat-led stories or when no photo fits.
- **Creator Spotlight carousel (two slides):**
  - Slide 1: the creator cut out on brand pink, their name in huge type behind them, stat stickers, the hook line and their handle.
  - Slide 2: detail. Headline fact, stats, three "why brands work with them" points, and how to book.
  - The creator block in the story file drives both slides.
- Headline on the card: 60 characters or fewer where possible.

### AI imagery

Use AI-generated images when no library photo matches the headline. Rules:

- **Illustrations only.** Never present an AI image as a photo of a real event, place on a specific date, person or product.
- **No real people, no real brands.** No logos, no signage, no recognisable faces, no brand packaging.
- **Always labelled.** Set `"aiImage": true` in the story file. The card and the article caption then say "AI illustration".
- **Match the headline's idea, not the news event.** For example, "a sponsor lounge at a night festival", not "Dream Weekend 2026".
- **Our own photos win.** When a real Screenshot photo fits, use it.
- Save generated images in `assets/bigger-picture/library/ai/` and add them to `library.json` with `"ai": true`.

## 9. Story file

One JSON file per story in `content/bigger-picture/`, named `YYYY-MM-DD-slug.json`. See existing files for fields. Set `"draft": true` until approved. Build with `python3 tools/bigger_picture.py`.
