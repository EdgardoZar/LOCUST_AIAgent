# Jenkins Pipeline Parameters - Quick Reference

## 🚀 Script Generation Pipeline

### **Required Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `SCENARIO_NAME` | String | (empty) | Name of the test scenario |
| `SCENARIO_JSON` | Text | (empty) | JSON configuration for the scenario |

### **Optional Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `TARGET_HOST` | String | `https://api.example.com` | Target host URL |
| `API_TOKEN` | Password | (empty) | API token for authentication |
| `ENVIRONMENT` | Choice | `dev` | Target environment (dev/staging/prod) |
| `USERS` | String | `10` | Number of concurrent users |
| `SPAWN_RATE` | String | `2` | Users spawned per second |
| `RUN_TIME` | String | `5m` | Test duration |
| `MIN_WAIT` | String | `1000` | Min wait time (ms) |
| `MAX_WAIT` | String | `5000` | Max wait time (ms) |
| `GENERATE_HTML_REPORT` | Boolean | `true` | Generate HTML report |
| `GENERATE_CSV_REPORT` | Boolean | `true` | Generate CSV report |
| `LOG_LEVEL` | String | `INFO` | Logging level |
| `GIT_COMMIT_MESSAGE` | String | (empty) | Custom commit message |

---

## 🎯 Test Execution Pipeline

### **Required Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `SELECTED_SCRIPT` | String | (auto) | Script to run (auto-populated) |

### **Optional Parameters**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `TARGET_HOST` | String | `https://api.example.com` | Target host URL |
| `API_TOKEN` | Password | (empty) | API token for authentication |
| `ENVIRONMENT` | Choice | `dev` | Target environment |
| `USERS` | String | `10` | Number of concurrent users |
| `SPAWN_RATE` | String | `2` | Users spawned per second |
| `RUN_TIME` | String | `5m` | Test duration |
| `MIN_WAIT` | String | `1000` | Min wait time (ms) |
| `MAX_WAIT` | String | `5000` | Max wait time (ms) |
| `USE_LLM_ANALYSIS` | Boolean | `false` | Enable LLM analysis |
| `GENERATE_HTML_REPORT` | Boolean | `true` | Generate HTML report |
| `GENERATE_CSV_REPORT` | Boolean | `true` | Generate CSV report |
| `LOG_LEVEL` | String | `INFO` | Logging level |
| `MAX_AVG_RESPONSE_TIME` | String | `2000` | Max avg response time (ms) |
| `MIN_SUCCESS_RATE` | String | `95` | Min success rate (%) |
| `MIN_REQUESTS_PER_SEC` | String | `10` | Min requests per second |
| `TEST_DESCRIPTION` | String | (empty) | Test run description |
| `TEST_TAGS` | String | (empty) | Test run tags |

---

## ⚡ Quick Setup Commands

### **Script Generation - Minimal Setup**
```
SCENARIO_NAME: "API Health Check"
SCENARIO_JSON: [Copy from examples/sample_scenario_for_jenkins.json]
TARGET_HOST: "https://rickandmortyapi.com"
ENVIRONMENT: "dev"
USERS: "5"
RUN_TIME: "2m"
```

### **Test Execution - Minimal Setup**
```
SELECTED_SCRIPT: [auto-populated]
TARGET_HOST: "https://rickandmortyapi.com"
ENVIRONMENT: "dev"
USERS: "5"
RUN_TIME: "2m"
TEST_DESCRIPTION: "Smoke test"
TEST_TAGS: "smoke,api"
```

---

## 🔧 Parameter Types Reference

| Type | Use For | Example |
|------|---------|---------|
| **String Parameter** | Single line text | `SCENARIO_NAME`, `TARGET_HOST` |
| **Text Parameter** | Multi-line text | `SCENARIO_JSON` |
| **Choice Parameter** | Dropdown selection | `ENVIRONMENT` |
| **Boolean Parameter** | True/False | `GENERATE_HTML_REPORT` |
| **Password Parameter** | Sensitive data | `API_TOKEN` |

---

## 📊 Common Values

### **Environments**
- `dev` - Development environment
- `staging` - Staging environment  
- `prod` - Production environment

### **Log Levels**
- `DEBUG` - Detailed debugging information
- `INFO` - General information (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages only

### **Time Formats**
- `30s` - 30 seconds
- `1m` - 1 minute
- `5m` - 5 minutes
- `1h` - 1 hour

### **User Load Examples**
| Scenario | Users | Spawn Rate | Run Time |
|----------|-------|------------|----------|
| **Smoke Test** | 1-5 | 1 | 1-2m |
| **Load Test** | 10-50 | 2-5 | 5-10m |
| **Stress Test** | 100-500 | 10-20 | 10-30m |
| **Spike Test** | 1000+ | 50+ | 5-15m |

---

## 🚨 Performance Thresholds

### **Response Time Guidelines**
- **Excellent**: < 500ms
- **Good**: 500ms - 1s
- **Acceptable**: 1s - 2s
- **Poor**: > 2s

### **Success Rate Guidelines**
- **Production**: ≥ 99%
- **Staging**: ≥ 95%
- **Development**: ≥ 90%

### **Requests Per Second**
- **Light Load**: 1-10 RPS
- **Medium Load**: 10-50 RPS
- **Heavy Load**: 50-200 RPS
- **Extreme Load**: 200+ RPS

---

## 🔍 Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| **Parameter not found** | Check spelling and case sensitivity |
| **Invalid JSON** | Use online JSON validator |
| **No scripts available** | Run script generation first |
| **Git permission denied** | Check Jenkins Git credentials |
| **Test fails immediately** | Verify TARGET_HOST is accessible |
| **High response times** | Reduce user count or increase wait times |
| **Low success rate** | Check API endpoints and authentication |

---

## 📝 Best Practices Checklist

- [ ] Start with minimal parameters
- [ ] Use descriptive scenario names
- [ ] Validate JSON before running
- [ ] Test with small user counts first
- [ ] Monitor resource usage
- [ ] Use tags for organization
- [ ] Document parameter changes
- [ ] Keep scenarios in version control

---

## 🎯 Next Steps

1. **Configure Script Generation Pipeline** with required parameters
2. **Generate your first script** using sample JSON
3. **Configure Test Execution Pipeline** with generated script
4. **Run initial smoke test** with minimal load
5. **Scale up gradually** based on results
6. **Monitor and optimize** performance thresholds

---

*For detailed step-by-step instructions, see [JENKINS_PIPELINE_PARAMETERS_GUIDE.md](./JENKINS_PIPELINE_PARAMETERS_GUIDE.md)* 