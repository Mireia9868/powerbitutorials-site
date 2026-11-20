import { ADSENSE_CLIENT } from "../consts";

/**
 * AdSense 广告单元 ID 是否可用：必须是非全 0 的 10 位数字。
 * 之前的占位符 "0000000000" 会让 <ins> 渲染出来却永远没有广告填充，
 * 只留下一块 min-height 的空白，所以这里直接把占位符挡掉。
 */
export function isValidAdSlot(slot: string | undefined): boolean {
  if (!ADSENSE_CLIENT || !slot) return false;
  return /^\d{10}$/.test(slot) && !/^0+$/.test(slot);
}
