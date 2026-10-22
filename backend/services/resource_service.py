# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 经核验的专业心理健康资源服务 (Resource Navigation Service)
严格遵循 PRD 3.0 第 8.8 / 10.8 / 18.11 节规范：
- 每条资源均有明确地区、服务类型、核验日期与有效状态
- 拒绝虚假合作，真实透明
"""
import json
from typing import List, Dict, Any, Optional
from backend.config import settings

class ResourceService:
    def __init__(self):
        self.resources: List[Dict[str, Any]] = []
        self._load_resources()

    def _load_resources(self):
        res_file = settings.KNOWLEDGE_DIR / "resources" / "mental_health_resources.json"
        if res_file.exists():
            with open(res_file, "r", encoding="utf-8") as f:
                self.resources = json.load(f)

    def list_resources(
        self,
        region: Optional[str] = None,
        service_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """按地区与类型筛选有效专业资源"""
        results = []
        for r in self.resources:
            if r.get("status") != "verified":
                continue
            if region and region != "全部" and region != "全国":
                # 如果指定特定省市，匹配该地区或全国通用热线
                if r.get("region") != region and r.get("region") != "全国":
                    continue
            if service_type and service_type != "all":
                if r.get("service_type") != service_type:
                    continue
            results.append(r)
        return results

    def get_available_regions(self) -> List[str]:
        regions = set()
        for r in self.resources:
            reg = r.get("region")
            if reg:
                regions.add(reg)
        return sorted(list(regions))

resource_service = ResourceService()
