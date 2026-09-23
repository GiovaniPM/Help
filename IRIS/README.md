# InterSystems IRIS — Índice de Rotas de Implantação

Este documento é o ponto de entrada para as arquiteturas de implantação do
InterSystems IRIS documentadas neste repositório. Cada rota é um caminho
independente e autocontido — com seu próprio documento de arquitetura,
manifests, diagramas e procedimento de implantação — organizado por ordem
crescente de maturidade operacional: de um único container local até um
cluster produtivo em nuvem com IAM federado.

| # | Rota | Orquestração | Escopo | Status |
|---|---|---|---|---|
| 1 | [Kubernetes Local](#1-kubernetes-local-manifests-nativos) | Manifests K8s nativos | Dev / testes locais | Validado |
| 2 | [Kubernetes com IKO](#2-kubernetes-com-iko) | IKO (operador oficial) | Dev avançado, homologação, produção | Proposto |
| 3 | [AKS + Workload Identity](#3-aks--microsoft-entra-id-workload-identity) | IKO + IAM federado (Azure) | Produção em nuvem | Proposto |

As rotas 1→3 formam uma linha de evolução: a Rota 3 assume a Rota 2 como
base de implantação do IRIS e adiciona uma camada de identidade; a Rota 2
resolve as lacunas de HA/automação deixadas pela Rota 1. Nenhuma rota é um
substituto universal das demais — a escolha depende do ambiente alvo
(seção [Comparativo Detalhado](#comparativo-detalhado) ao final).

---

## 1. Kubernetes Local (manifests nativos)

**Documento completo:** [IRIS-Kubernetes-Local-Arquitetura-Solucao.md](Kubernets/Rota%201/IRIS-Kubernetes-Local-Arquitetura-Solucao.md)

### Desenho de arquitetura

![Arquitetura: IRIS no Kubernetes local — Deployment/Pod/Container, PVC iris-data e Service ClusterIP, com acesso via kubectl port-forward](Kubernets/Rota%201/iris-k8s-architecture.svg)

### Resumo executivo

Implantação do InterSystems IRIS Community Edition em um cluster
Kubernetes local (Docker Desktop, `kind` ou `minikube`), usando manifests
YAML padrão — `Deployment`, `Service`, `PersistentVolumeClaim` — sem
depender do IKO (InterSystems Kubernetes Operator). Remove as barreiras de
entrada da Rota 2 (conta WRC, registry privado) mantendo o mesmo modelo
mental de Kubernetes, ao custo de abrir mão das automações de ciclo de
vida (mirroring, sharding, scaling) do operador oficial. Por isso, também
**não é recomendada para produção**.

---

## 2. Kubernetes com IKO

**Documento completo:** [IRIS-Kubernetes-IKO-Arquitetura-Solucao.md](Kubernets/Rota%202/IRIS-Kubernetes-IKO-Arquitetura-Solucao.md)

### Desenho de arquitetura

![Arquitetura: IRIS no Kubernetes via IKO — operador observa o CR IrisCluster e cria/gerencia StatefulSet de dados (mirrored), Deployments de compute e webgateway, arbiter, PVCs e Services](Kubernets/Rota%202/iris-k8s-iko-architecture.svg)

### Resumo executivo

Implantação do InterSystems IRIS utilizando o **IKO — InterSystems
Kubernetes Operator**, o operador oficial mantido pela InterSystems. Ao
invés de manifests aplicados diretamente (Rota 1), o usuário declara a
topologia desejada em um único Custom Resource (`IrisCluster`) e o IKO
reconcilia automaticamente `StatefulSet` (com mirroring), `Deployment`s de
compute e webgateway, PVCs e Services. Em troca das automações de HA,
sharding e scaling, introduz dependências adicionais: conta no WRC,
acesso a registry privado (ICR) e um processo de instalação via Helm mais
elaborado. É o caminho de evolução natural a partir da Rota 1 para
cenários de homologação e produção.

---

## 3. AKS + Microsoft Entra ID Workload Identity

**Documento completo:** [IRIS-Kubernetes-AKS-WorkloadIdentity-Arquitetura-Solucao.md](Kubernets/Rota%203/IRIS-Kubernetes-AKS-WorkloadIdentity-Arquitetura-Solucao.md)

### Desenho de arquitetura

![Arquitetura: IRIS em AKS com Workload Identity — Microsoft Entra ID (UAMI, Federated Identity Credential, role assignments), recursos Azure (Key Vault, Storage Account, ACR), e dentro do cluster a ServiceAccount federada, o Job de bootstrap de segredos, o CronJob de backup e o IrisCluster reaproveitado da Rota 2](Kubernets/Rota%203/iris-aks-workload-identity-architecture.svg)

### Resumo executivo

Implantação do InterSystems IRIS em um cluster **AKS (Azure Kubernetes
Service)**, adicionando **IAM nativo do Azure** — Microsoft Entra ID
Workload Identity — para eliminar credenciais estáticas no acesso a
**Azure Key Vault** (licença e senha administrativa), **Azure Storage**
(destino de backup) e **Azure Container Registry** (imagens). Parte da
Rota 2 como base de implantação do IRIS em si — o `IrisCluster` continua
gerenciado pelo IKO sem alterações no CRD — e adiciona, por cima, uma
camada de identidade federada via OIDC entre o cluster e o Entra ID,
respondendo diretamente à limitação de gestão de segredos apontada na
Rota 2. É a rota indicada para ambientes produtivos em nuvem que exigem
eliminação de segredos de longa duração armazenados no cluster.

---

## Comparativo Detalhado

| Critério | 1. Kubernetes Local | 2. Kubernetes + IKO | 3. AKS + Workload Identity |
|---|---|---|---|
| **Orquestrador** | Kubernetes (manifests nativos) | Kubernetes + IKO (operador oficial) | AKS + IKO + IAM federado (Entra ID) |
| **Escopo recomendado** | Dev / testes locais | Dev avançado, homologação, produção | Produção em nuvem |
| **Status neste repositório** | Validado | Proposto (pendente validação com WRC/ICR) | Proposto (pendente validação em AKS) |
| **Imagem** | `iris-community` (Docker Hub, pública) | `iris` licenciado (ICR, privado) | `iris` licenciado (ICR, opcionalmente espelhado no ACR) |
| **Requer conta WRC / registry privado** | Não | Sim (pacote IKO + imagens ICR) | Sim (herdado da Rota 2) |
| **Alta disponibilidade** | Nenhuma (1 réplica, sem redundância) | Nativa (`mirrored: true` + arbiter, failover automático) | Igual à Rota 2 (HA do IRIS não é o foco desta rota) |
| **Escalonamento** | Manual (`kubectl scale`, sem automação) | Automatizado pelo operador (compute nodes, sharding) | Igual à Rota 2 |
| **Persistência** | `PersistentVolumeClaim` único (5Gi) | PVCs gerenciados pelo operador por componente | PVCs da Rota 2 (inalterados) |
| **Exposição de rede** | `ClusterIP` + `kubectl port-forward` | `ClusterIP` ou `LoadBalancer` (`serviceTemplate`) | Igual à Rota 2; foco desta rota é IAM, não rede |
| **Gestão de credenciais** | Senha padrão definida na 1ª execução, sem cofre | Secrets Kubernetes criados manualmente (`kubectl create secret`), texto plano em trânsito | Segredos centralizados no Azure Key Vault; sem credenciais estáticas no cluster (token OIDC federado, ~1h) |
| **Backup / DR** | Não coberto (requer estratégia dedicada) | Mirroring cobre HA local; backup entre clusters não coberto | `CronJob` diário automatizado para Azure Storage via identidade federada (sem SAS/chave) |
| **Complexidade operacional** | Baixa (3 manifests YAML) | Média-alta (Helm, CRDs, múltiplos secrets, reconciliação assíncrona) | Alta (tudo da Rota 2 + UAMI, Federated Identity Credential, RBAC do Azure, Jobs auxiliares) |
| **Pré-requisitos de ferramentas** | Docker Desktop/`kind`/`minikube` + `kubectl` | `kubectl` + Helm 3 + conta WRC | Tudo da Rota 2 + Azure CLI (`az`) com permissões de Entra ID |
| **Tempo até ambiente funcional** | Minutos | Horas (obtenção de pacote, secrets, Helm, CR) | Adicional de ~1h sobre a Rota 2 (propagação da federated credential inclusa) |
| **Observabilidade** | Não coberta | Não coberta (inclui eventos do operador) | Não coberta (inclui Sign-in logs da UAMI no Entra ID) |
| **Quando escolher** | Time pequeno testando o modelo Kubernetes sem custo de licença/registry | Cargas de trabalho que exigem HA, scaling e automação de ciclo de vida, com acesso ao WRC | Produção em Azure exigindo eliminação de segredos estáticos e auditoria de acesso a Key Vault/Storage |

### Notas de leitura da tabela

- **Rota 1** é o ponto de partida sem HA nem operador — a diferença para
  a Rota 2 é apenas a ausência de automação de ciclo de vida — e é
  explicitamente **não recomendada para produção** pelo respectivo
  documento.
- **Rota 2** é o primeiro salto de maturidade real: introduz o operador
  oficial e HA nativa, mas ao custo de dependências externas (WRC/ICR) e
  complexidade operacional.
- **Rota 3** não substitui a Rota 2 — ela é aplicada **sobre** uma Rota 2
  já implantada, adicionando exclusivamente a camada de IAM/segredos. Por
  isso, várias linhas da tabela acima replicam o valor da Rota 2 (HA,
  escalonamento, rede), já que esses aspectos não são alterados por ela.
