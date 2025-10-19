# Contribuindo

Obrigado por contribuir! Leia primeiro o README (seção "Como contribuir"). Abaixo um resumo prático.

## Fluxo de trabalho
1) Fork e clone o repositório (se externo)
2) Crie uma branch: `feature/minha-feature` ou `fix/minha-correcao`
3) Desenvolva incrementalmente com commits claros
4) Rode `make ci-local` e verifique se tudo está verde
5) Abra um Pull Request com contexto e checklist

## Convenções
- Branches: `feature/`, `fix/`, `docs/`, `chore/`, `ci/`
- Commits curtos e no imperativo (Ex.: "Add X", "Fix Y"). Prefixos opcionais: `Feat:`, `Fix:`, `Docs:`, `DX:`, `CI:`, `Refactor:`, `Chore:`

## Antes do PR
- Execute `make ci-local` (checks, flake8, testes, coverage XML/HTML)
- Se houver mudanças de modelo: garanta `makemigrations` + `migrate`
- Atualize README/docs e help de comandos quando necessário
- Escreva/atualize testes para as regras de negócio

## Templates
- Pull Request: `.github/PULL_REQUEST_TEMPLATE.md`
- Issues: `.github/ISSUE_TEMPLATE/bug_report.md` e `.github/ISSUE_TEMPLATE/feature_request.md`

## Dicas
- Use `make demo` ou `make demo-admin` para preparar um ambiente local rápido.
- Prefere containers? `make docker-demo` fará build + up + migrate + admin + seed.
- Precisou resetar tudo? `make reset` (cuidado, apaga db.sqlite3 e media/).

## Conduta
Este projeto segue o [Contributor Covenant v2.1](./CODE_OF_CONDUCT.md).
