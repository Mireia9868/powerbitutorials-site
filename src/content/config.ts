import { defineCollection, z } from "astro:content";

const tutorials = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    category: z.enum([
      "dax",
      "power-query",
      "data-modeling",
      "visualization",
      "time-intelligence",
    ]),
    difficulty: z.enum(["Beginner", "Intermediate", "Advanced"]),
    tags: z.array(z.string()).default([]),
    author: z.string().default("Power BI Tutorials Team"),
    heroImage: z.string().optional(),
    draft: z.boolean().default(false),
    featured: z.boolean().default(false),
  }),
});

export const collections = { tutorials };
