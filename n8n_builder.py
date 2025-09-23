# modern_n8n_templates.py - قوالب متوافقة مع n8n Cloud الحديث
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

def create_modern_webhook_to_sheets() -> Dict[str, Any]:
    """إنشاء workflow حديث متوافق مع n8n Cloud"""
    
    webhook_id = str(uuid.uuid4())
    sheets_id = str(uuid.uuid4())
    
    return {
        "meta": {
            "templateCreatedBy": "Enhanced AI Bot",
            "instanceId": str(uuid.uuid4())
        },
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "contact-form",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": webhook_id,
                "name": "Form Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": webhook_id
            },
            {
                "parameters": {
                    "resource": "sheet",
                    "operation": "appendOrUpdate",
                    "documentId": {
                        "__rl": True,
                        "value": "={{$env.GOOGLE_SHEET_ID}}",
                        "mode": "id"
                    },
                    "sheetName": {
                        "__rl": True,
                        "value": "طلبات2024",
                        "mode": "list"
                    },
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "اسم العميل": "={{ $json.name }}",
                            "الشركة": "={{ $json.company }}",
                            "الإيميل": "={{ $json.email }}",
                            "الخدمة نوع": "={{ $json.service_type }}",
                            "الميزانية المتوقعة": "={{ $json.budget }}",
                            "الطلب رقم": "={{ $json.request_id }}",
                            "Request_ID": "={{ 'REQ-' + new Date().getTime().toString() }}",
                            "Timestamp": "={{ new Date().toISOString() }}"
                        },
                        "matchingColumns": [],
                        "schema": []
                    },
                    "options": {}
                },
                "id": sheets_id,
                "name": "Save to Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [460, 300]
            }
        ],
        "connections": {
            webhook_id: {
                "main": [
                    [
                        {
                            "node": sheets_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "versionId": str(uuid.uuid4()),
        "id": str(uuid.uuid4()),
        "name": "Custom Form to طلبات2024",
        "tags": [
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "form"
            },
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "webhook"
            },
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "sheets"
            }
        ],
        "pinData": {},
        "staticData": {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "triggerCount": 1
    }

def create_modern_form_with_email() -> Dict[str, Any]:
    """نموذج مع إيميل - متوافق مع n8n Cloud الحديث"""
    
    webhook_id = str(uuid.uuid4())
    process_id = str(uuid.uuid4())
    sheets_id = str(uuid.uuid4())
    email_id = str(uuid.uuid4())
    respond_id = str(uuid.uuid4())
    
    return {
        "meta": {
            "templateCreatedBy": "Enhanced AI Bot",
            "instanceId": str(uuid.uuid4())
        },
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST", 
                    "path": "service-request",
                    "responseMode": "onReceived",
                    "options": {}
                },
                "id": webhook_id,
                "name": "Service Request",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "webhookId": webhook_id
            },
            {
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "ticket_id",
                                "value": "={{ 'TICKET-' + new Date().getTime().toString() }}"
                            },
                            {
                                "name": "priority", 
                                "value": "={{ $json.budget && parseInt($json.budget) > 10000 ? 'عالية' : 'عادية' }}"
                            },
                            {
                                "name": "follow_up_date",
                                "value": "={{ new Date(Date.now() + 3*24*60*60*1000).toISOString() }}"
                            }
                        ]
                    },
                    "options": {}
                },
                "id": process_id,
                "name": "Process Request Data",
                "type": "n8n-nodes-base.set",
                "typeVersion": 3,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "resource": "sheet",
                    "operation": "appendOrUpdate", 
                    "documentId": {
                        "__rl": True,
                        "value": "={{$env.SERVICE_SHEET_ID}}",
                        "mode": "id"
                    },
                    "sheetName": {
                        "__rl": True,
                        "value": "طلبات الخدمة",
                        "mode": "list"
                    },
                    "columns": {
                        "mappingMode": "defineBelow",
                        "value": {
                            "رقم التذكرة": "={{ $('Process Request Data').item.json.ticket_id }}",
                            "اسم العميل": "={{ $json.name }}",
                            "الشركة": "={{ $json.company }}",
                            "الإيميل": "={{ $json.email }}",
                            "نوع الخدمة": "={{ $json.service_type }}",
                            "الميزانية": "={{ $json.budget }}",
                            "الأولوية": "={{ $('Process Request Data').item.json.priority }}",
                            "الوصف": "={{ $json.description }}",
                            "تاريخ التقديم": "={{ new Date().toISOString() }}",
                            "موعد المتابعة": "={{ $('Process Request Data').item.json.follow_up_date }}",
                            "الحالة": "جديد"
                        },
                        "matchingColumns": [],
                        "schema": []
                    },
                    "options": {}
                },
                "id": sheets_id,
                "name": "Save Service Request", 
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "send",
                    "toEmail": "={{ $json.email }}",
                    "subject": "تأكيد استلام طلب الخدمة - {{ $('Process Request Data').item.json.ticket_id }}",
                    "emailType": "text",
                    "message": "عزيزي/عزيزتي {{ $json.name }},\n\nتم استلام طلب الخدمة الخاص بك بنجاح.\n\nتفاصيل الطلب:\n• رقم الطلب: {{ $('Process Request Data').item.json.ticket_id }}\n• نوع الخدمة: {{ $json.service_type }}\n• الأولوية: {{ $('Process Request Data').item.json.priority }}\n• موعد المتابعة المتوقع: {{ $('Process Request Data').item.json.follow_up_date.slice(0,10) }}\n\nسيتم التواصل معك خلال 24-48 ساعة لمناقشة التفاصيل.\n\nشكراً لثقتك بنا،\nفريق الخدمات",
                    "options": {}
                },
                "id": email_id,
                "name": "Send Confirmation Email",
                "type": "n8n-nodes-base.gmail", 
                "typeVersion": 2,
                "position": [900, 300]
            },
            {
                "parameters": {
                    "respondBody": "{\"success\": true, \"message\": \"تم استلام طلبك بنجاح\", \"ticket_id\": \"{{ $('Process Request Data').item.json.ticket_id }}\"}",
                    "options": {}
                },
                "id": respond_id,
                "name": "Respond Success",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1120, 300]
            }
        ],
        "connections": {
            webhook_id: {
                "main": [
                    [
                        {
                            "node": process_id,
                            "type": "main", 
                            "index": 0
                        }
                    ]
                ]
            },
            process_id: {
                "main": [
                    [
                        {
                            "node": sheets_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            sheets_id: {
                "main": [
                    [
                        {
                            "node": email_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            email_id: {
                "main": [
                    [
                        {
                            "node": respond_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "versionId": str(uuid.uuid4()),
        "id": str(uuid.uuid4()),
        "name": "Service Request Form with Auto-Email and Ticket ID",
        "tags": [
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "service"
            },
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "email"
            },
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "automation"
            }
        ],
        "pinData": {},
        "staticData": {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "triggerCount": 1
    }

def create_modern_scheduled_report() -> Dict[str, Any]:
    """تقرير مجدول - متوافق مع n8n Cloud الحديث"""
    
    cron_id = str(uuid.uuid4())
    fetch_id = str(uuid.uuid4())
    process_id = str(uuid.uuid4())
    email_id = str(uuid.uuid4())
    
    return {
        "meta": {
            "templateCreatedBy": "Enhanced AI Bot",
            "instanceId": str(uuid.uuid4())
        },
        "nodes": [
            {
                "parameters": {
                    "rule": {
                        "interval": [
                            {
                                "field": "hour",
                                "value": 9
                            },
                            {
                                "field": "minute", 
                                "value": 0
                            }
                        ]
                    }
                },
                "id": cron_id,
                "name": "Daily at 9 AM",
                "type": "n8n-nodes-base.cron",
                "typeVersion": 1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "method": "GET",
                    "url": "={{$env.SALES_API_ENDPOINT}}/daily-stats",
                    "authentication": "genericCredentialType",
                    "genericAuthType": "httpHeaderAuth",
                    "options": {
                        "headers": {
                            "values": [
                                {
                                    "name": "Authorization",
                                    "value": "Bearer {{$env.API_TOKEN}}"
                                }
                            ]
                        }
                    }
                },
                "id": fetch_id,
                "name": "Fetch Sales Data",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "jsCode": "// معالجة بيانات المبيعات\nconst data = $input.all()[0].json;\nconst yesterday = new Date();\nyesterday.setDate(yesterday.getDate() - 1);\n\nconst report = {\n  date: yesterday.toISOString().split('T')[0],\n  total_sales: data.total_sales || 0,\n  total_orders: data.total_orders || 0,\n  avg_order_value: (data.total_sales || 0) / (data.total_orders || 1),\n  top_products: data.top_products?.slice(0, 5) || [],\n  growth_rate: data.growth_rate || 0,\n  processed_at: new Date().toISOString()\n};\n\nreturn [report];",
                    "options": {}
                },
                "id": process_id,
                "name": "Process Sales Analytics",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "send",
                    "toEmail": "={{$env.SALES_TEAM_EMAIL}}",
                    "subject": "تقرير المبيعات اليومي - {{ $json.date }}",
                    "emailType": "html",
                    "message": "<div dir='rtl' style='font-family: Arial, sans-serif;'>\n<h2>تقرير المبيعات اليومي</h2>\n<p><strong>التاريخ:</strong> {{ $json.date }}</p>\n<hr>\n<h3>المقاييس الرئيسية</h3>\n<ul>\n<li><strong>إجمالي المبيعات:</strong> ${{ $json.total_sales.toLocaleString() }}</li>\n<li><strong>إجمالي الطلبات:</strong> {{ $json.total_orders }}</li>\n<li><strong>متوسط قيمة الطلب:</strong> ${{ $json.avg_order_value.toFixed(2) }}</li>\n<li><strong>معدل النمو:</strong> {{ $json.growth_rate }}%</li>\n</ul>\n<h3>أفضل المنتجات</h3>\n<ol>{{ $json.top_products.map(p => `<li>${p.name}: ${p.sales} وحدة</li>`).join('') }}</ol>\n<p><em>تم إنشاء التقرير في: {{ $json.processed_at }}</em></p>\n</div>",
                    "options": {}
                },
                "id": email_id,
                "name": "Send Sales Report",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [900, 300]
            }
        ],
        "connections": {
            cron_id: {
                "main": [
                    [
                        {
                            "node": fetch_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            fetch_id: {
                "main": [
                    [
                        {
                            "node": process_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            process_id: {
                "main": [
                    [
                        {
                            "node": email_id,
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "versionId": str(uuid.uuid4()),
        "id": str(uuid.uuid4()),
        "name": "Daily Sales Report with Analytics",
        "tags": [
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "schedule"
            },
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "report"
            },
            {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "name": "analytics"
            }
        ],
        "pinData": {},
        "staticData": {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "triggerCount": 1
    }

# القوالب الحديثة
MODERN_N8N_TEMPLATES = {
    "webhook_to_sheets": create_modern_webhook_to_sheets,
    "form_with_email": create_modern_form_with_email,
    "scheduled_report": create_modern_scheduled_report
}

def get_modern_template(template_name: str, custom_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """الحصول على قالب حديث متوافق مع n8n Cloud"""
    if template_name in MODERN_N8N_TEMPLATES:
        template = MODERN_N8N_TEMPLATES[template_name]()
        
        if custom_data:
            return customize_modern_template(template, custom_data)
        return template
    else:
        return create_modern_webhook_to_sheets()

def customize_modern_template(template: Dict[str, Any], custom_data: Dict[str, Any]) -> Dict[str, Any]:
    """تخصيص القالب الحديث بناءً على البيانات المخصصة"""
    
    # تخصيص الاسم
    if 'sheet_name' in custom_data:
        template['name'] = f"Custom Form to {custom_data['sheet_name']}"
        
        # تحديث أسماء الجداول في العقد
        for node in template['nodes']:
            if node.get('type') == 'n8n-nodes-base.googleSheets':
                params = node.get('parameters', {})
                if 'sheetName' in params:
                    params['sheetName']['value'] = custom_data['sheet_name']
    
    # تخصيص الحقول
    if 'data_fields' in custom_data:
        for node in template['nodes']:
            if node.get('type') == 'n8n-nodes-base.googleSheets':
                params = node.get('parameters', {})
                if 'columns' in params and 'value' in params['columns']:
                    # إضافة الحقول المخصصة
                    columns = params['columns']['value']
                    for field_key, field_name in custom_data['data_fields'].items():
                        columns[field_name] = f"={{{{ $json.{field_key} }}}}"
    
    # إضافة منطق الأعمال
    if 'business_logic' in custom_data:
        business_logic = custom_data['business_logic']
        
        if 'generate_id' in business_logic:
            # إضافة توليد ID تلقائي
            for node in template['nodes']:
                if node.get('type') == 'n8n-nodes-base.googleSheets':
                    params = node.get('parameters', {})
                    if 'columns' in params and 'value' in params['columns']:
                        params['columns']['value']['Request_ID'] = "={{ 'REQ-' + new Date().getTime().toString() }}"
    
    # تحديث التواريخ والـ IDs
    template['updatedAt'] = datetime.now().isoformat()
    template['versionId'] = str(uuid.uuid4())
    
    return template
