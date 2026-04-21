let cache = null;

export const loadIcons = async () => {
  if (cache) return cache;
  const mod = await import(/* webpackChunkName: "mdi-meta" */ "@mdi/svg/meta.json");
  const raw = mod.default || mod;
  cache = raw.map((entry) => {
    const aliases = entry.aliases || [];
    const tags = entry.tags || [];
    const searchText = [entry.name, ...aliases, ...tags].join(" ").toLowerCase();
    return { name: entry.name, aliases, tags, searchText };
  });
  return cache;
};

const VALID = /^[a-z0-9]+(-[a-z0-9]+)*$/;
export const isValidIconName = (name) => typeof name === "string" && VALID.test(name);

export const SIZE_IDS = ["sm", "md", "lg", "xl"];
export const DEFAULT_SIZE = "sm";
export const isValidSize = (size) => typeof size === "string" && SIZE_IDS.includes(size);