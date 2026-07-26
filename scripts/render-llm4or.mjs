import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const dataPath = path.join(repoRoot, "research-works.json");
const htmlPath = path.join(repoRoot, "LLM4OR.html");
const sitemapPath = path.join(repoRoot, "sitemap.xml");

const startMarker = "<!-- RESEARCH_WORKS_START -->";
const endMarker = "<!-- RESEARCH_WORKS_END -->";
const jsonLdStartMarker = "<!-- RESEARCH_JSON_LD_START -->";
const jsonLdEndMarker = "<!-- RESEARCH_JSON_LD_END -->";
const collectionUrl = "https://linjianghao.com/LLM4OR.html";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function joinAuthors(authors) {
  if (!Array.isArray(authors) || authors.length === 0) return "";
  if (authors.length === 1) return `${authors[0]}.`;
  if (authors.length === 2) return `${authors[0]} and ${authors[1]}.`;
  return `${authors.slice(0, -1).join(", ")}, and ${authors.at(-1)}.`;
}

function renderStatus(status) {
  if (!status) return "";
  if (status.text) return escapeHtml(status.text);
  return `${escapeHtml(status.prefix)} <em>${escapeHtml(status.emphasis)}</em>${escapeHtml(status.suffix)}`;
}

function renderLinks(links, indent) {
  const items = (links || []).map((link) => (
    `${indent}  <a href="${escapeHtml(link.url)}" target="_blank" rel="noopener">${escapeHtml(link.label)}</a>`
  ));
  return [`${indent}<div class="links">`, ...items, `${indent}</div>`].join("\n");
}

function renderKeywords(keywords, indent) {
  const items = (keywords || []).map((keyword) => (
    `${indent}  <span class="keyword">${escapeHtml(keyword)}</span>`
  ));
  return [`${indent}<div class="keywords">`, ...items, `${indent}</div>`].join("\n");
}

function renderAbstract(abstract, indent) {
  const safeAbstract = escapeHtml(abstract);
  return [
    `${indent}<details class="abstract-toggle">`,
    `${indent}  <summary><span class="abstract-preview"><span class="abstract-preview-text">${safeAbstract}</span><span class="abstract-preview-dots">...</span></span></summary>`,
    `${indent}  <p class="abstract-text">${safeAbstract}</p>`,
    `${indent}</details>`
  ].join("\n");
}

function renderField(label, content, indent) {
  return [
    `${indent}<div class="field">`,
    `${indent}  <div class="field-label">${escapeHtml(label)}</div>`,
    content,
    `${indent}</div>`
  ].join("\n");
}

function renderWork(work, indent) {
  const bodyIndent = `${indent}    `;
  return [
    `${indent}<details class="work" id="${escapeHtml(work.id)}" open>`,
    `${indent}  <summary>`,
    `${indent}    <span class="work-heading">`,
    `${indent}      <h2>${escapeHtml(work.title)}</h2>`,
    `${indent}      <p class="authors">${escapeHtml(joinAuthors(work.authors))}</p>`,
    `${indent}      <p class="venue">${renderStatus(work.status)}</p>`,
    `${indent}    </span>`,
    `${indent}    <span class="caret" aria-hidden="true">&gt;</span>`,
    `${indent}  </summary>`,
    `${indent}  <div class="work-body">`,
    renderField("TLDR", `${bodyIndent}  <p>${escapeHtml(work.tldr)}</p>`, bodyIndent),
    renderField("Abstract", renderAbstract(work.abstract, `${bodyIndent}  `), bodyIndent),
    renderField("Keywords", renderKeywords(work.keywords, `${bodyIndent}  `), bodyIndent),
    renderField("Links", renderLinks(work.links, `${bodyIndent}  `), bodyIndent),
    `${indent}  </div>`,
    `${indent}</details>`
  ].join("\n");
}

function renderStage(stage) {
  const indent = "      ";
  return [
    `${indent}<details class="stage" id="${escapeHtml(stage.id)}" open>`,
    `${indent}  <summary>`,
    `${indent}    <span class="stage-number">${escapeHtml(stage.number)}</span>`,
    `${indent}    <span class="stage-copy">`,
    `${indent}      <span class="stage-title">${escapeHtml(stage.title)}</span>`,
    `${indent}      <span class="stage-intro">${escapeHtml(stage.intro)}</span>`,
    `${indent}    </span>`,
    `${indent}    <span class="caret" aria-hidden="true">&gt;</span>`,
    `${indent}  </summary>`,
    `${indent}  <div class="stage-body">`,
    ...(stage.works || []).map((work) => renderWork(work, `${indent}    `)),
    `${indent}  </div>`,
    `${indent}</details>`
  ].join("\n");
}

function buildJsonLd(data) {
  const works = (data.stages || []).flatMap((stage) => stage.works || []);
  const organizationId = `${collectionUrl}#organization`;
  const editorId = "https://linjianghao.com/#jianghao-lin";
  const collectionId = `${collectionUrl}#collection`;
  const worksId = `${collectionUrl}#research-works`;

  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "CollectionPage",
        "@id": collectionId,
        url: collectionUrl,
        name: "From Optimization Automation to Innovation: Building OR-Native AI in the LLM Era",
        description: "Research works on OR-native AI in the LLM era, from optimization automation to innovation.",
        inLanguage: "en",
        creator: { "@id": organizationId },
        editor: { "@id": editorId },
        mainEntity: { "@id": worksId },
        about: [
          { "@type": "Thing", name: "Large Language Models" },
          { "@type": "Thing", name: "Operations Research" },
          { "@type": "Thing", name: "OR-Native AI" }
        ]
      },
      {
        "@type": "Organization",
        "@id": organizationId,
        name: "Institute of Intelligent Computing, Shanghai Jiao Tong University",
        alternateName: "IIC@SJTU",
        url: "https://iic.sjtu.edu.cn/"
      },
      {
        "@type": "Person",
        "@id": editorId,
        name: "Jianghao Lin",
        url: "https://linjianghao.com/",
        affiliation: { "@id": organizationId }
      },
      {
        "@type": "ItemList",
        "@id": worksId,
        name: "LLM4OR Research Works",
        numberOfItems: works.length,
        itemListElement: works.map((work, index) => {
          const paperLink = (work.links || []).find((link) => link.label === "Paper");
          const article = {
            "@type": "ScholarlyArticle",
            "@id": `${collectionUrl}#${work.id}`,
            url: `${collectionUrl}#${work.id}`,
            name: work.title,
            author: (work.authors || []).map((name) => ({ "@type": "Person", name })),
            abstract: work.abstract,
            keywords: work.keywords || [],
            isPartOf: { "@id": collectionId }
          };
          if (paperLink) article.sameAs = paperLink.url;

          return {
            "@type": "ListItem",
            position: index + 1,
            item: article
          };
        })
      }
    ]
  };
}

function renderJsonLd(data) {
  const serialized = JSON.stringify(buildJsonLd(data), null, 2)
    .replaceAll("<", "\\u003c")
    .split("\n")
    .map((line) => `    ${line}`)
    .join("\n");

  return [
    jsonLdStartMarker,
    '  <script type="application/ld+json">',
    serialized,
    "  </script>",
    `  ${jsonLdEndMarker}`
  ].join("\n");
}

function shanghaiDate() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).formatToParts(new Date());
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  return `${values.year}-${values.month}-${values.day}`;
}

function updateSitemap(date) {
  const sitemap = fs.readFileSync(sitemapPath, "utf8");
  const entryPattern = /(<loc>https:\/\/linjianghao\.com\/LLM4OR\.html<\/loc>\s*<lastmod>)[^<]+(<\/lastmod>)/;
  if (!entryPattern.test(sitemap)) {
    throw new Error("Could not find the LLM4OR entry in sitemap.xml");
  }
  const nextSitemap = sitemap.replace(entryPattern, `$1${date}$2`);
  if (nextSitemap !== sitemap) fs.writeFileSync(sitemapPath, nextSitemap);
}

const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
const html = fs.readFileSync(htmlPath, "utf8");
const markerPattern = new RegExp(`${startMarker}[\\s\\S]*?${endMarker}`);
const jsonLdMarkerPattern = new RegExp(`${jsonLdStartMarker}[\\s\\S]*?${jsonLdEndMarker}`);

if (!markerPattern.test(html)) {
  throw new Error("Could not find the generated research-work markers in LLM4OR.html");
}
if (!jsonLdMarkerPattern.test(html)) {
  throw new Error("Could not find the generated JSON-LD markers in LLM4OR.html");
}

const renderedWorks = (data.stages || []).map(renderStage).join("\n");
const generatedBlock = `${startMarker}\n${renderedWorks}\n    ${endMarker}`;
const nextHtml = html
  .replace(markerPattern, generatedBlock)
  .replace(jsonLdMarkerPattern, renderJsonLd(data));

if (nextHtml === html) {
  console.log("LLM4OR.html is already synchronized with research-works.json.");
} else {
  fs.writeFileSync(htmlPath, nextHtml);
  updateSitemap(shanghaiDate());
  console.log("Updated LLM4OR.html and its sitemap lastmod from research-works.json.");
}
