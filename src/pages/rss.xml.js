import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import { SITE_TITLE, SITE_DESCRIPTION } from "../consts";

export async function GET(context) {
  const tutorials = (await getCollection("tutorials", ({ data }) => !data.draft))
    .sort((a, b) => b.data.pubDate.getTime() - a.data.pubDate.getTime());

  return rss({
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    site: context.site,
    items: tutorials.map((t) => ({
      title: t.data.title,
      description: t.data.description,
      pubDate: t.data.pubDate,
      link: `/tutorials/${t.slug}/`,
      categories: [t.data.category],
      author: t.data.author,
    })),
    customData: `<language>en-us</language>`,
  });
}
