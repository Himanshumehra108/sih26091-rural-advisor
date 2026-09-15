import states from "india-location-data/src/data/states.json";
import districts from "india-location-data/src/data/districts.json";
import blocks from "india-location-data/src/data/blocks.json";

const clean = (value) => String(value || "").replace(/\s+/g, " ").trim();

export const INDIA_STATES = states
  .map((item) => clean(item.name))
  .filter(Boolean)
  .sort((a, b) => a.localeCompare(b));

const stateById = new Map(states.map((item) => [item.id, clean(item.name)]));

export const DISTRICTS_BY_STATE = districts.reduce((result, item) => {
  const stateName = stateById.get(item.stateId);
  const districtName = clean(item.name);
  if (!stateName || !districtName) return result;
  if (!result[stateName]) result[stateName] = [];
  result[stateName].push(districtName);
  return result;
}, {});

Object.values(DISTRICTS_BY_STATE).forEach((items) => items.sort((a, b) => a.localeCompare(b)));

const districtById = new Map(districts.map((item) => [item.id, clean(item.name)]));
export const BLOCKS_BY_DISTRICT = blocks.reduce((result, item) => {
  const districtName = districtById.get(item.districtId);
  const blockName = clean(item.name);
  if (!districtName || !blockName) return result;
  if (!result[districtName]) result[districtName] = [];
  result[districtName].push(blockName);
  return result;
}, {});

Object.values(BLOCKS_BY_DISTRICT).forEach((items) => {
  const unique = [...new Set(items)];
  items.splice(0, items.length, ...unique.sort((a, b) => a.localeCompare(b)));
});

export function findOfficialState(value) {
  const normalized = clean(value).toLowerCase().replace(/\s*\([^)]*\)$/, "");
  return INDIA_STATES.find((state) => {
    const candidate = state.toLowerCase().replace(/\s*\([^)]*\)$/, "");
    return candidate === normalized;
  }) || "";
}

export function findOfficialDistrict(state, value) {
  const normalized = clean(value).toLowerCase();
  return (DISTRICTS_BY_STATE[state] || []).find(
    (district) => district.toLowerCase() === normalized
  ) || "";
}
