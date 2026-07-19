import { config, fields, collection } from "@keystatic/core";

// 本地开发用 local 存储；生产部署切到 github 存储（见 README）
// 生产配置示例:
//   storage: { kind: 'github', repo: { owner: 'your-org', name: 'daxguide-site' } }
export default config({
  storage: { kind: "local" },
  ui: {
    brand: { name: "DAX Guide CMS" },
    navigation: {
      Content: ["tutorials"],
    },
  },
  collections: {
    tutorials: collection({
      label: "Tutorials",
      slugField: "title",
      path: "src/content/tutorials/*",
      entryLayout: "content",
      format: { contentField: "content" },
      columns: ["title", "category", "pubDate", "difficulty"],
      searchField: "title",
      schema: {
        title: fields.slug({
          name: { label: "Title", validation: { length: { min: 1 } } },
          slug: {
            // slug = 文件名，使用 kebab-case
            generate: (title) =>
              title
                .toLowerCase()
                .replace(/[^a-z0-9\s-]/g, "")
                .trim()
                .replace(/\s+/g, "-")
                .replace(/-+/g, "-"),
            validation: { length: { min: 1 } },
          },
        }),
        description: fields.text({
          label: "Description (SEO meta, 1-2 sentences)",
          multiline: true,
          validation: { length: { min: 20, max: 200 } },
        }),
        pubDate: fields.date({
          label: "Publish Date",
          validation: { isRequired: true },
        }),
        updatedDate: fields.date({ label: "Updated Date (optional)" }),
        category: fields.select({
          label: "Category",
          options: [
            { label: "DAX Formulas", value: "dax" },
            { label: "Power Query", value: "power-query" },
            { label: "Data Modeling", value: "data-modeling" },
            { label: "Visualization", value: "visualization" },
            { label: "Time Intelligence", value: "time-intelligence" },
          ],
          defaultValue: "dax",
        }),
        difficulty: fields.select({
          label: "Difficulty",
          options: [
            { label: "Beginner", value: "Beginner" },
            { label: "Intermediate", value: "Intermediate" },
            { label: "Advanced", value: "Advanced" },
          ],
          defaultValue: "Beginner",
        }),
        tags: fields.array(fields.text({ label: "Tag" }), {
          label: "Tags",
          itemLabel: (props) => props.value,
        }),
        author: fields.text({
          label: "Author",
          defaultValue: "DAX Guide Editorial Team",
        }),
        featured: fields.checkbox({
          label: "Featured on homepage",
          defaultValue: false,
        }),
        heroImage: fields.text({
          label: "Hero Image URL (optional, e.g. /images/tutorials/foo.png)",
        }),
        draft: fields.checkbox({
          label: "Draft (excluded from published site)",
          defaultValue: false,
        }),
        content: fields.document({
          label: "Tutorial Content (Markdown)",
          formatting: true,
          dividers: true,
          links: true,
          images: {
            directory: "public/images/tutorials",
            publicPath: "/images/tutorials/",
          },
        }),
      },
    }),
  },
});
