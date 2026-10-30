# Raya deploy history

Append-only log of prompts pushed live via `scripts/raya_deploy.py deploy`.
Newest entries at the bottom. This records what went live, when, and the
pre-deploy snapshot label to roll back to — the deploy-side twin of
`versions/<Agent>/HISTORY.md` (which logs edits, not deploys).

This is **not** an edit log — prompt *edits* go in each agent's `CHANGELOG.md`.
A deploy ships whatever is already on disk; it does not change prompt content.

Format:
`YYYY-MM-DD HH:MM:SS · <env> · <target-id> · <raya_agent_id> · <file> · sha256:<8> · snapshot:<label> · <result>`

---
2026-07-18 19:59:01 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch
2026-07-18 19:59:01 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch
2026-07-19 16:54:19 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · MPL-feature
2026-07-19 16:54:19 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · MPL-feature
2026-07-19 17:22:03 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:22:03 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · profile-wording
2026-07-19 17:32:47 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · mpl-english+wording-fix
2026-07-19 17:32:47 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · mpl-english+wording-fix
2026-07-19 17:32:47 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch · mpl-english+wording-fix
2026-07-19 17:32:47 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch · mpl-english+wording-fix
2026-07-20 08:54:16 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · verified=True · via=api-patch · inbound-agegender+mpl-fix
2026-07-20 09:05:34 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:05:34 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · verified=True · via=api-patch · agegender-recheck+mpl-out
2026-07-20 09:35:08 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:40f2e811 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_093507 · deployed
2026-07-20 09:35:08 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:1b2d9f01 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_093508 · deployed
2026-07-20 09:35:09 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5c016d78 · snapshot:pre-deploy-kkb-hi-in-2026-07-20_093508 · deployed
2026-07-20 09:35:09 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c02d871 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_093509 · deployed
2026-07-20 09:35:10 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:ad87aa65 · snapshot:pre-deploy-maya-hi-out-2026-07-20_093509 · deployed
2026-07-20 09:35:10 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:6e03a5d0 · snapshot:pre-deploy-maya-hi-in-2026-07-20_093510 · deployed
2026-07-20 09:48:22 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:fa884e10 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_094822 · deployed
2026-07-20 09:48:23 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:90c99ff0 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_094823 · deployed
2026-07-20 09:48:24 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:dca43c3a · snapshot:pre-deploy-kkb-hi-in-2026-07-20_094823 · deployed
2026-07-20 09:48:24 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:6f0b0ee6 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_094824 · deployed
2026-07-20 09:48:25 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:58554ce4 · snapshot:pre-deploy-maya-hi-out-2026-07-20_094825 · deployed
2026-07-20 09:48:25 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:d9ba68b2 · snapshot:pre-deploy-maya-hi-in-2026-07-20_094825 · deployed
2026-07-20 10:00:57 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:6bd77a6e · snapshot:pre-deploy-maya-hi-in-2026-07-20_100057 · deployed
2026-07-20 10:00:58 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:a930a02a · snapshot:pre-deploy-maya-hi-out-2026-07-20_100058 · deployed
2026-07-20 10:11:49 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b93e866b · snapshot:pre-deploy-maya-hi-in-2026-07-20_101149 · deployed
2026-07-20 10:11:50 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:0b553014 · snapshot:pre-deploy-maya-hi-out-2026-07-20_101150 · deployed
2026-07-20 10:26:02 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:5f420f09 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_102601 · deployed
2026-07-20 10:26:02 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:caf1c0f7 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_102602 · deployed
2026-07-20 10:26:04 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:9c852ae9 · snapshot:pre-deploy-kkb-hi-in-2026-07-20_102602 · deployed
2026-07-20 10:26:05 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:f373cf9c · snapshot:pre-deploy-kkb-kn-in-2026-07-20_102604 · deployed
2026-07-20 10:26:06 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:324ecfd0 · snapshot:pre-deploy-maya-hi-out-2026-07-20_102605 · deployed
2026-07-20 10:26:06 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:56b8bd0c · snapshot:pre-deploy-maya-hi-in-2026-07-20_102606 · deployed
2026-07-20 10:35:40 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_103539 · deployed
2026-07-20 10:35:40 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_103540 · deployed
2026-07-20 10:35:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:pre-deploy-kkb-hi-in-2026-07-20_103541 · deployed
2026-07-20 10:35:43 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_103542 · deployed
2026-07-20 10:35:43 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b8f8eab1 · snapshot:pre-deploy-maya-hi-out-2026-07-20_103543 · deployed
2026-07-20 10:35:44 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:03e71608 · snapshot:pre-deploy-maya-hi-in-2026-07-20_103543 · deployed
2026-07-20 10:35:44 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:pre-deploy-dkb-hi-out-2026-07-20_103544 · deployed
2026-07-20 10:35:45 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:pre-deploy-dkb-kn-out-2026-07-20_103544 · deployed
2026-07-20 10:48:31 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:fd2eda94 · snapshot:pre-deploy-maya-hi-in-2026-07-20_104830 · deployed
2026-07-20 10:48:32 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:6b675eb1 · snapshot:pre-deploy-maya-hi-out-2026-07-20_104831 · deployed
2026-07-20 11:34:59 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:pre-deploy-maya-hi-in-2026-07-20_113458 · deployed
2026-07-20 11:34:59 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:pre-deploy-maya-hi-out-2026-07-20_113459 · deployed
2026-07-20 12:36:39 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:pre-deploy-maya-hi-in-2026-07-20_123639 · deployed
2026-07-20 12:38:16 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:38:17 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:- · skip-in-sync
2026-07-20 12:38:19 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:- · skip-in-sync
2026-07-20 12:38:19 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:- · skip-in-sync
2026-07-20 12:38:20 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:pre-deploy-maya-hi-out-2026-07-20_123819 · deployed
2026-07-20 12:38:20 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:- · skip-in-sync
2026-07-20 12:38:20 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:- · skip-in-sync
2026-07-20 12:38:21 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:- · skip-in-sync
2026-07-20 12:39:06 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:39:06 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:- · skip-in-sync
2026-07-20 12:39:07 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:- · skip-in-sync
2026-07-20 12:39:08 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:- · skip-in-sync
2026-07-20 12:39:09 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:- · skip-in-sync
2026-07-20 12:39:35 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:40:01 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ea448ac5 · snapshot:- · skip-in-sync
2026-07-20 12:40:01 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3cee2a34 · snapshot:- · skip-in-sync
2026-07-20 12:40:02 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:82a042c3 · snapshot:- · skip-in-sync
2026-07-20 12:40:02 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ae8e9d61 · snapshot:- · skip-in-sync
2026-07-20 12:40:02 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e911b925 · snapshot:- · skip-in-sync
2026-07-20 12:40:03 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bc23c4ff · snapshot:- · skip-in-sync
2026-07-20 12:40:03 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:ddc84e64 · snapshot:- · skip-in-sync
2026-07-20 12:40:03 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:3f200181 · snapshot:- · skip-in-sync
2026-07-20 13:47:58 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:acc65013 · snapshot:pre-deploy-kkb-hi-out-2026-07-20_134756 · deployed
2026-07-20 13:47:59 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:847f7e06 · snapshot:pre-deploy-kkb-kn-out-2026-07-20_134758 · deployed
2026-07-20 13:48:01 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:e96cac5a · snapshot:pre-deploy-kkb-hi-in-2026-07-20_134800 · deployed
2026-07-20 13:48:03 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:a7cb1235 · snapshot:pre-deploy-kkb-kn-in-2026-07-20_134802 · deployed
2026-07-20 13:48:03 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:4058e05e · snapshot:pre-deploy-maya-hi-out-2026-07-20_134803 · deployed
2026-07-20 13:48:05 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:2ce4b7a5 · snapshot:pre-deploy-maya-hi-in-2026-07-20_134804 · deployed
2026-07-20 17:56:37 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:50437850 · snapshot:- · dry-run
2026-07-20 18:14:05 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:dad55800 · snapshot:pre-deploy-maya-hi-out-2026-07-20_181405 · deployed
2026-07-20 18:30:04 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:1a830d75 · snapshot:pre-deploy-maya-hi-out-2026-07-20_183000 · deployed
2026-07-20 18:49:54 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:9cf2877d · snapshot:pre-deploy-maya-hi-out-2026-07-20_184954 · deployed
2026-07-20 18:57:42 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:883c5e4d · snapshot:pre-deploy-maya-hi-out-2026-07-20_185739 · deployed
2026-07-20 19:08:40 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:64474648 · snapshot:pre-deploy-maya-hi-out-2026-07-20_190839 · deployed
2026-07-20 19:12:55 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:3b474e2c · snapshot:pre-deploy-maya-hi-out-2026-07-20_191253 · deployed
2026-07-20 19:17:40 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:2340b864 · snapshot:pre-deploy-maya-hi-out-2026-07-20_191738 · deployed
2026-07-20 19:23:15 · prod · maya-out-memory · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Memory.md · sha256:9c8f4e68 · snapshot:- · skip-in-sync
2026-07-20 19:24:21 · prod · maya-out-memory · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Memory.md · sha256:9c8f4e68 · snapshot:pre-deploy-maya-out-memory-2026-07-20_192418 · deployed
2026-07-20 19:24:46 · prod · maya-in-memory · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Memory.md · sha256:9c8f4e68 · snapshot:pre-deploy-maya-in-memory-2026-07-20_192446 · deployed
2026-07-22 11:40:34 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:cb374109 · snapshot:pre-deploy-kkb-hi-out-2026-07-22_114033 · deployed
2026-07-22 11:40:35 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:ba8d8907 · snapshot:pre-deploy-kkb-kn-out-2026-07-22_114035 · deployed
2026-07-22 12:47:45 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:330ae247 · snapshot:pre-deploy-kkb-hi-out-2026-07-22_124742 · deployed
2026-07-22 12:47:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:1b76f201 · snapshot:pre-deploy-kkb-kn-out-2026-07-22_124746 · deployed
2026-07-22 12:58:06 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:3310c32d · snapshot:pre-deploy-kkb-hi-in-2026-07-22_125804 · deployed
2026-07-22 12:58:07 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:4669eb7d · snapshot:pre-deploy-kkb-kn-in-2026-07-22_125807 · deployed
2026-07-22 13:00:43 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:d7dbb322 · snapshot:pre-deploy-maya-hi-out-2026-07-22_130038 · deployed
2026-07-22 13:30:21 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:16ef42f1 · snapshot:pre-deploy-dkb-hi-out-2026-07-22_133021 · deployed
2026-07-22 13:30:21 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:a5dbc7c1 · snapshot:pre-deploy-dkb-kn-out-2026-07-22_133021 · deployed
2026-07-22 13:47:15 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:236af7ef · snapshot:pre-deploy-kkb-hi-out-2026-07-22_134709 · deployed
2026-07-22 13:47:16 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:358d3607 · snapshot:pre-deploy-kkb-kn-out-2026-07-22_134715 · deployed
2026-07-22 16:40:09 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:74c900b1 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_164005 · deployed
2026-07-22 16:40:13 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:e73018d5 · snapshot:pre-deploy-kkb-kn-in-2026-07-22_164011 · deployed
2026-07-22 17:19:13 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:23268495 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_171859 · deployed
2026-07-22 17:19:25 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ee29d045 · snapshot:pre-deploy-kkb-kn-in-2026-07-22_171917 · deployed
2026-07-22 17:24:37 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:fef972a0 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_172359 · deployed
2026-07-22 17:25:06 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:09b414ed · snapshot:pre-deploy-kkb-kn-in-2026-07-22_172446 · deployed
2026-07-22 17:28:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:2ced8c59 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_172748 · deployed
2026-07-22 17:29:17 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c98ea27 · snapshot:pre-deploy-kkb-kn-in-2026-07-22_172853 · deployed
2026-07-22 20:15:56 · prod · kkb-hi-in · 08001508-0146-467b-a35f-e8754a7aeff5 · KKB/KKB Placeholder Inbound.md · sha256:09e410ba · snapshot:pre-deploy-kkb-hi-in-2026-07-22_201555 · deployed
2026-07-22 20:18:09 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c98ea27 · snapshot:- · skip-in-sync
2026-07-22 20:18:10 · prod · kkb-hi-in · 08001508-0146-467b-a35f-e8754a7aeff5 · KKB/KKB Placeholder Inbound.md · sha256:09e410ba · snapshot:- · skip-in-sync
2026-07-22 22:31:43 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:61162c10 · snapshot:pre-deploy-kkb-hi-in-2026-07-22_223142 · deployed
2026-07-22 22:33:07 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:9d98a31c · snapshot:pre-deploy-kkb-kn-in-2026-07-22_223215 · deployed
2026-07-23 11:46:07 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:2ced8c59 · snapshot:pre-deploy-kkb-hi-in-2026-07-23_114607 · deployed
2026-07-23 11:47:50 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7c98ea27 · snapshot:pre-deploy-kkb-kn-in-2026-07-23_114736 · FAILED-http-520
2026-07-27 00:56:40 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:9a31a31e · snapshot:pre-deploy-kkb-kn-in-2026-07-27_005640 · deployed
2026-07-27 00:56:41 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:7be20a47 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_005641 · deployed
2026-07-27 00:56:42 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:9747ea41 · snapshot:pre-deploy-kkb-kn-out-2026-07-27_005642 · deployed
2026-07-27 00:56:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5ada6513 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_005642 · deployed
2026-07-27 00:56:44 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:d48b7e78 · snapshot:pre-deploy-maya-hi-out-2026-07-27_005643 · deployed
2026-07-27 00:56:44 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:209847d5 · snapshot:pre-deploy-maya-hi-in-2026-07-27_005644 · deployed
2026-07-27 01:15:23 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:c483d75a · snapshot:pre-deploy-kkb-hi-in-2026-07-27_011523 · deployed
2026-07-27 01:15:23 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:db86351f · snapshot:pre-deploy-kkb-kn-in-2026-07-27_011523 · deployed
2026-07-27 01:36:58 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b257cb42 · snapshot:pre-deploy-maya-hi-out-2026-07-27_013658 · deployed
2026-07-27 01:36:58 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:e94b03fb · snapshot:pre-deploy-maya-hi-in-2026-07-27_013658 · deployed
2026-07-27 01:46:38 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:f91622b0 · snapshot:pre-deploy-kkb-kn-in-2026-07-27_014638 · deployed
2026-07-27 01:46:39 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:23feff4d · snapshot:pre-deploy-kkb-kn-out-2026-07-27_014639 · deployed
2026-07-27 01:46:39 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:2ca73049 · snapshot:pre-deploy-maya-hi-out-2026-07-27_014639 · deployed
2026-07-27 02:24:32 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:0fd202e7 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_022432 · deployed
2026-07-27 02:24:32 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2c7b11af · snapshot:pre-deploy-kkb-kn-out-2026-07-27_022432 · deployed
2026-07-27 02:24:33 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:a66c02c8 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_022433 · deployed
2026-07-27 02:24:33 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:46e12c33 · snapshot:pre-deploy-kkb-kn-in-2026-07-27_022433 · deployed
2026-07-27 02:31:39 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e68d7622 · snapshot:pre-deploy-maya-hi-out-2026-07-27_023139 · deployed
2026-07-27 02:31:39 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:68f5224e · snapshot:pre-deploy-maya-hi-in-2026-07-27_023139 · deployed
2026-07-27 02:31:40 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:08c7b4c6 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_023140 · deployed
2026-07-27 02:31:40 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:3b8cf2bc · snapshot:pre-deploy-kkb-kn-out-2026-07-27_023140 · deployed
2026-07-27 02:31:41 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5ed86a87 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_023140 · deployed
2026-07-27 02:31:41 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:a8d5170b · snapshot:pre-deploy-kkb-kn-in-2026-07-27_023141 · deployed
2026-07-27 12:16:33 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:62967128 · snapshot:- · dry-run
2026-07-27 12:16:41 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:62967128 · snapshot:pre-deploy-kkb-hi-in-2026-07-27_121640 · deployed
2026-07-27 12:16:41 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:e1a58e0a · snapshot:pre-deploy-kkb-kn-in-2026-07-27_121641 · deployed
2026-07-27 14:00:45 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:3fda09a9 · snapshot:pre-deploy-maya-hi-in-2026-07-27_140044 · deployed
2026-07-27 14:00:45 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:79f48c0e · snapshot:pre-deploy-kkb-hi-in-2026-07-27_140045 · deployed
2026-07-27 14:00:46 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:74b89498 · snapshot:pre-deploy-kkb-kn-in-2026-07-27_140045 · deployed
2026-07-27 14:00:46 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:71019e54 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_140046 · deployed
2026-07-27 14:00:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:150433f1 · snapshot:pre-deploy-kkb-kn-out-2026-07-27_140046 · deployed
2026-07-27 14:00:47 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:d82f163c · snapshot:pre-deploy-maya-hi-out-2026-07-27_140047 · deployed
2026-07-27 15:00:50 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1600f0a5 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_150049 · deployed
2026-07-27 15:02:01 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1a442549 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_150201 · deployed
2026-07-27 15:43:58 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c1e80d67 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_154358 · deployed
2026-07-27 16:06:45 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:614e7c61 · snapshot:pre-deploy-kkb-hi-out-2026-07-27_160645 · deployed
2026-07-27 16:06:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2944cf61 · snapshot:pre-deploy-kkb-kn-out-2026-07-27_160645 · deployed
2026-07-27 16:50:56 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:7be0fe89 · snapshot:pre-deploy-kkb-kn-signals-2026-07-27_165056 · deployed
2026-07-29 15:26:26 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:9d63073a · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_152625 · deployed
2026-07-29 15:48:42 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f48ae8bb · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_154842 · deployed
2026-07-29 16:02:03 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:6db42235 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_160203 · deployed
2026-07-29 16:37:27 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:4f730d45 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_163727 · deployed
2026-07-29 16:59:54 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:087e7f50 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_165954 · deployed
2026-07-29 17:07:25 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:d9fe6d82 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_170725 · deployed
2026-07-29 17:16:56 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:6da03377 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_171656 · deployed
2026-07-29 18:48:37 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:81bda6be · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_184837 · deployed
2026-07-29 20:05:07 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:75466c7f · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_200506 · deployed
2026-07-29 21:12:22 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:a155cb82 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_211221 · deployed
2026-07-29 21:19:37 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:9296eb64 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_211937 · deployed
2026-07-29 21:19:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:d7a7600f · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_211937 · deployed
2026-07-29 21:45:52 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c93c8df3 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_214552 · deployed
2026-07-29 21:45:52 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:efd79e0c · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_214552 · deployed
2026-07-29 22:02:33 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c0668ec2 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_220232 · deployed
2026-07-29 22:02:33 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:2a3d8900 · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_220233 · deployed
2026-07-29 22:14:44 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:303a9b3a · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_221444 · deployed
2026-07-29 22:14:46 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:185d278b · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_221445 · deployed
2026-07-29 22:17:33 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f28bfa3c · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_221733 · deployed
2026-07-29 22:17:34 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f5e6e997 · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_221733 · deployed
2026-07-29 23:27:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:546b08ee · snapshot:pre-deploy-kkb-hi-signals-2026-07-29_232738 · deployed
2026-07-29 23:27:38 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:b1ab4030 · snapshot:pre-deploy-kkb-kn-signals-2026-07-29_232738 · deployed
2026-07-30 00:35:34 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:9b92a60e · snapshot:pre-deploy-kkb-hi-in-2026-07-30_003534 · deployed
2026-07-30 00:39:43 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:1b20779a · snapshot:pre-deploy-kkb-hi-in-2026-07-30_003943 · deployed
2026-07-30 00:48:10 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:9c47ef45 · snapshot:pre-deploy-kkb-kn-in-2026-07-30_004810 · deployed
2026-07-30 02:41:08 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:6edaca1f · snapshot:pre-deploy-dkb-hi-out-2026-07-30_024108 · deployed
2026-07-30 02:41:09 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:835f4705 · snapshot:pre-deploy-dkb-kn-out-2026-07-30_024109 · deployed
2026-07-30 02:45:28 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:3d8606c8 · snapshot:pre-deploy-kkb-hi-out-2026-07-30_024527 · deployed
2026-07-30 02:45:28 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:0c195839 · snapshot:pre-deploy-kkb-kn-out-2026-07-30_024528 · deployed
2026-07-30 03:10:10 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:8e2bbd24 · snapshot:pre-deploy-maya-hi-out-2026-07-30_031010 · deployed
2026-07-30 03:11:09 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:98a33823 · snapshot:pre-deploy-maya-hi-in-2026-07-30_031109 · deployed
2026-07-30 03:23:13 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:674f31cb · snapshot:pre-deploy-kkb-hi-out-2026-07-30_032312 · deployed
2026-07-30 03:23:15 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:e4062597 · snapshot:pre-deploy-kkb-kn-out-2026-07-30_032314 · deployed
2026-07-30 04:01:47 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:fe80aeb4 · snapshot:pre-deploy-kkb-hi-out-2026-07-30_040146 · deployed
2026-07-30 04:01:47 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:bb86fbaf · snapshot:pre-deploy-kkb-kn-out-2026-07-30_040147 · deployed
2026-07-30 (config) · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · TOOL api_details endpoint change (get_profile jobs.onest.seeker→job-up.seeker; apply_job onest-lite-bap→up-onest-lite-bap) — **REVERTED same session**. WRONG: Kannada bot INTENTIONALLY uses the Karnataka endpoints (jobs.onest.seeker / onest-lite-bap); the up-/job-up hosts are UP-specific. Owner correction: "karnataka doesn't use those endpoints." Restored from snapshot:raya/snapshots/kkb-kn-out.tools.pre-endpoint-fix.json · instructions preserved (74483ch) · read-back verified back on Karnataka endpoints. NET: no live change. Apply-404 on the Karnataka BAP endpoint stands as a BACKEND issue to flag (not a prompt/config fix).
2026-07-31 11:15:09 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:edf4eada · snapshot:- · dry-run
2026-07-31 11:15:28 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:edf4eada · snapshot:pre-deploy-kkb-hi-out-2026-07-31_111527 · deployed
2026-07-31 11:15:29 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:b1cfb4db · snapshot:pre-deploy-kkb-kn-out-2026-07-31_111528 · deployed
2026-07-31 11:15:29 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:43bbc939 · snapshot:pre-deploy-kkb-hi-signals-2026-07-31_111529 · deployed
2026-07-31 11:15:30 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:4026e547 · snapshot:pre-deploy-kkb-kn-signals-2026-07-31_111530 · deployed
2026-07-31 11:15:31 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:d0591afa · snapshot:pre-deploy-maya-hi-out-2026-07-31_111530 · deployed
2026-07-31 (repurpose) · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · REPURPOSED from maya-hi-combined → Maya Hindi Signals: PATCHed name+instructions(112k)+4 Signals tools (cloned from kkb-hi-signals) · snapshot:raya/snapshots/904f333f.tools.pre-repurpose.json · read-back verified (Signals endpoints live) · voice-test in progress
2026-07-31 (repurpose) · prod · kkb-hi-in-signals · 3f521174 · KKB Inbound Signals (Hi) · repurposed ex-combined + Signals tools + real-jobs inventory
2026-07-31 (repurpose) · prod · kkb-kn-in-signals · f38da775 · KKB Inbound Signals (Kn) · repurposed + kn Signals tools + real-jobs inventory
2026-07-31 (create) · prod · maya-hi-in-signals · 1c24feda · Maya Inbound Signals · new agent (clone df99f501) + Signals tools + real-jobs inventory
2026-07-31 (repurpose) · prod · dkb-hi-signals · fabda71d · DKB Hindi Signals · Signals create_job/update_job (provider job_posting) + get_talent_insights; create_job curl-grounded (item f6c3d7bb)
2026-07-31 (repurpose) · prod · dkb-kn-signals · 847a85e2 · DKB Kannada Signals · same Signals provider tools
2026-08-04 17:46:09 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:7f606fac · snapshot:pre-deploy-kkb-kn-signals-2026-08-04_174608 · deployed
2026-08-04 17:46:09 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:aa98e2a0 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-04_174609 · deployed
2026-08-07 15:51:32 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:a619d0bd · snapshot:pre-deploy-kkb-kn-out-2026-08-07_155132 · deployed
2026-08-07 15:51:33 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:f06ec9f2 · snapshot:pre-deploy-kkb-hi-out-2026-08-07_155132 · deployed
2026-08-07 15:51:33 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:574cc9bc · snapshot:pre-deploy-kkb-kn-in-2026-08-07_155133 · deployed
2026-08-07 15:51:34 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:b921fa74 · snapshot:pre-deploy-kkb-hi-in-2026-08-07_155133 · deployed
2026-08-07 15:51:34 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f074dbd2 · snapshot:pre-deploy-kkb-kn-signals-2026-08-07_155134 · deployed
2026-08-07 15:51:35 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:2b7e299c · snapshot:pre-deploy-kkb-hi-signals-2026-08-07_155135 · deployed
2026-08-07 15:51:36 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:401e1148 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-07_155135 · deployed
2026-08-07 15:51:36 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:10f2f5ed · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-07_155136 · deployed
2026-08-07 17:27:31 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:bb84a4d6 · snapshot:pre-deploy-maya-hi-out-2026-08-07_172730 · deployed
2026-08-07 17:27:32 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:2cd6afe7 · snapshot:pre-deploy-maya-hi-in-2026-08-07_172731 · deployed
2026-08-07 17:27:33 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:b6b7466d · snapshot:pre-deploy-maya-hi-signals-2026-08-07_172732 · deployed
2026-08-07 17:27:34 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:296f98a6 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-07_172733 · deployed
2026-08-07 17:32:29 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:8d5e95e3 · snapshot:pre-deploy-maya-hi-signals-2026-08-07_173228 · deployed
2026-08-07 17:32:30 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:3c678392 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-07_173229 · deployed
2026-08-07 17:32:30 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:8263897f · snapshot:pre-deploy-maya-hi-out-2026-08-07_173230 · deployed
2026-08-07 17:32:31 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:123f6d8c · snapshot:pre-deploy-maya-hi-in-2026-08-07_173231 · deployed
2026-08-07 18:44:47 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:d36fccdb · snapshot:pre-deploy-maya-hi-signals-2026-08-07_184447 · deployed
2026-08-07 18:44:51 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:c3da3fe5 · snapshot:pre-deploy-maya-hi-out-2026-08-07_184451 · deployed
2026-08-07 18:44:53 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:d4ec6be2 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-07_184452 · deployed
2026-08-07 18:44:55 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:47f4beca · snapshot:pre-deploy-maya-hi-in-2026-08-07_184454 · deployed
2026-08-07 18:54:04 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:3d2cc5c6 · snapshot:pre-deploy-maya-hi-signals-2026-08-07_185404 · deployed
2026-08-07 18:54:05 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:109f2717 · snapshot:pre-deploy-maya-hi-out-2026-08-07_185405 · deployed
2026-08-07 18:54:06 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:194a8912 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-07_185406 · deployed
2026-08-07 18:54:07 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:3b869a99 · snapshot:pre-deploy-maya-hi-in-2026-08-07_185407 · deployed
2026-08-10 13:05:16 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:cc3f972b · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_130515 · deployed
2026-08-10 13:18:44 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:4aac8728 · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_131843 · deployed
2026-08-10 13:23:10 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:56e4f124 · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_132309 · deployed
2026-08-10 13:39:05 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:fa783cdd · snapshot:pre-deploy-kkb-kn-signals-2026-08-10_133905 · deployed
2026-08-10 13:39:06 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:adbbad7f · snapshot:pre-deploy-kkb-hi-out-2026-08-10_133905 · deployed
2026-08-10 13:39:06 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2f225c46 · snapshot:pre-deploy-kkb-kn-out-2026-08-10_133906 · deployed
2026-08-10 13:39:07 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:94b6c960 · snapshot:pre-deploy-maya-hi-signals-2026-08-10_133906 · deployed
2026-08-10 13:39:07 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b3d9a41a · snapshot:pre-deploy-maya-hi-out-2026-08-10_133907 · deployed
2026-08-10 13:39:07 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:2f2bdf90 · snapshot:pre-deploy-dkb-hi-signals-2026-08-10_133907 · deployed
2026-08-10 13:39:08 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:04f4c027 · snapshot:pre-deploy-dkb-kn-signals-2026-08-10_133908 · deployed
2026-08-10 13:39:08 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:0ae408fb · snapshot:pre-deploy-dkb-hi-out-2026-08-10_133908 · deployed
2026-08-10 13:39:09 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:a13458fc · snapshot:pre-deploy-dkb-kn-out-2026-08-10_133909 · deployed
2026-08-10 13:40:57 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f26a324e · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_134057 · deployed
2026-08-10 14:06:43 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:412ed1b7 · snapshot:pre-deploy-kkb-kn-signals-2026-08-10_140642 · deployed
2026-08-10 14:06:45 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:7d676f50 · snapshot:pre-deploy-kkb-hi-out-2026-08-10_140645 · deployed
2026-08-10 14:06:48 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:01da9475 · snapshot:pre-deploy-kkb-kn-out-2026-08-10_140648 · deployed
2026-08-10 14:06:51 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:9e2cbdd1 · snapshot:pre-deploy-kkb-hi-in-2026-08-10_140650 · deployed
2026-08-10 14:06:53 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:3c743b44 · snapshot:pre-deploy-kkb-kn-in-2026-08-10_140653 · deployed
2026-08-10 14:06:56 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:bfa19d15 · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-10_140656 · deployed
2026-08-10 14:06:58 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:c2c87f77 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-10_140658 · deployed
2026-08-10 14:07:01 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:912cff5d · snapshot:pre-deploy-maya-hi-signals-2026-08-10_140701 · deployed
2026-08-10 14:07:04 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:5289c205 · snapshot:pre-deploy-maya-hi-out-2026-08-10_140703 · deployed
2026-08-10 14:07:06 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:e5c73c35 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-10_140706 · deployed
2026-08-10 14:07:09 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:bcd38427 · snapshot:pre-deploy-maya-hi-in-2026-08-10_140709 · deployed
2026-08-10 14:24:15 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:2aea38c4 · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_142415 · deployed
2026-08-10 14:34:43 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:8ce3cfd1 · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_143443 · deployed

## 2026-08-10 — Caller memory turned ON fleet-wide, with each agent's memory prompt deployed

Config-only change (no prompt content edited), so it leaves no diff in the prompt files — recorded
here because it changes runtime behaviour on every live agent.

**Why.** `memory_enabled=true` makes the PLATFORM own `${contact_memory}`: it injects its own stored
per-caller memory and **discards whatever the campaign passes in `agent_args`**. Confirmed by a
controlled A/B on a scratch agent (same prompt, same args, one field changed): with the flag off the
bot read the supplied memory back verbatim; with it on the bot reported the memory as empty. The
campaigns send nothing in that field, so the platform is the right owner — but the flag is inert
without a memory-writer prompt, and the API rejects that combination outright:
`400 memory_instructions is required when memory_enabled is true`.

**Before:** six KKB agents had `memory_enabled=true` with `memory_instructions=NULL` — memory on,
nothing writing it, so an always-empty memory was injected on every call. Six Signals agents had
memory off entirely. Only DKB hi/kn outbound and Maya hi out/in had a working setup.

**Applied:**
- `KKB/KKB Memory.md` → kkb-hi-out, kkb-kn-out, kkb-hi-in, kkb-kn-in, kkb-hi-signals, kkb-kn-signals
- `KKB/KKB Memory.md` → kkb-hi-in-signals, kkb-kn-in-signals (also flipped `memory_enabled` on)
- `Maya/Maya Memory.md` → maya-hi-signals, maya-hi-in-signals (flag flipped on)
- `DKB/DKB Memory.md` → dkb-hi-signals, dkb-kn-signals (flag flipped on)
- TRRAIN hi/kn were created with memory on and their prompt already deployed.

**Result:** all 18 live conversation agents now have memory ON with a writer prompt. Verified that
all 20 conversation prompts carry the required `### Contact context` injection block verbatim first.

**Known drift, deliberately NOT touched:** `dkb-hi-out`'s live memory prompt is 8575 chars against
the repo's 8005 (`dkb-kn-out` live is 8005 and matches). Live is ahead on DKB Memory and needs a
proper reconcile — `scripts/raya_deploy.py pull` then commit — rather than being overwritten in
passing. The two DKB Signals agents received the repo version.

**Consequence for testing:** on a memory-enabled agent, passing `contact_memory` through
`agent_args` does nothing. Any memory-driven behaviour can only be tested with TWO sequential calls
to the same number — the first writing the memory, the second consuming it.
2026-08-10 18:55:14 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:dfb8bd20 · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_185513 · deployed
2026-08-10 18:57:12 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:9ec21902 · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_185712 · deployed
2026-08-10 19:50:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f1eb5938 · snapshot:pre-deploy-kkb-hi-signals-2026-08-10_195038 · deployed
2026-08-12 02:02:11 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:e627e7fa · snapshot:pre-deploy-kkb-hi-signals-2026-08-12_020211 · deployed
2026-08-12 02:02:14 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:dc375bb5 · snapshot:pre-deploy-kkb-kn-signals-2026-08-12_020213 · deployed
2026-08-12 02:08:11 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f1eb5938 · snapshot:pre-deploy-kkb-hi-signals-2026-08-12_020811 · deployed
2026-08-12 02:08:14 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:412ed1b7 · snapshot:pre-deploy-kkb-kn-signals-2026-08-12_020814 · deployed
2026-08-12 11:02:09 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:03707d0f · snapshot:pre-deploy-kkb-hi-out-2026-08-12_110209 · deployed
2026-08-12 11:02:12 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:42894c7c · snapshot:pre-deploy-kkb-kn-out-2026-08-12_110212 · deployed
2026-08-12 11:31:53 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:2be0783e · snapshot:pre-deploy-kkb-hi-out-2026-08-12_113153 · deployed
2026-08-12 11:31:56 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:fe21f27e · snapshot:pre-deploy-kkb-kn-out-2026-08-12_113155 · deployed
2026-08-12 11:31:58 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:21dcd5d5 · snapshot:pre-deploy-kkb-hi-in-2026-08-12_113158 · deployed
2026-08-12 11:32:01 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:0637c517 · snapshot:pre-deploy-kkb-kn-in-2026-08-12_113201 · deployed
2026-08-12 11:32:04 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:9bc7cd57 · snapshot:pre-deploy-kkb-hi-signals-2026-08-12_113204 · deployed
2026-08-12 11:32:07 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:bb957b06 · snapshot:pre-deploy-kkb-kn-signals-2026-08-12_113206 · deployed
2026-08-12 11:32:10 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:a372dadb · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-12_113209 · deployed
2026-08-12 11:32:12 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:6892e746 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-12_113212 · deployed
2026-08-12 11:32:15 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:9b4b4fd1 · snapshot:pre-deploy-maya-hi-out-2026-08-12_113215 · deployed
2026-08-12 11:32:18 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:2ec86595 · snapshot:pre-deploy-maya-hi-in-2026-08-12_113218 · deployed
2026-08-12 11:32:21 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:f7950a15 · snapshot:pre-deploy-maya-hi-signals-2026-08-12_113220 · deployed
2026-08-12 11:32:24 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:56579da4 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-12_113223 · deployed
2026-08-12 13:17:50 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:31396ae8 · snapshot:pre-deploy-kkb-hi-in-2026-08-12_131749 · deployed
2026-08-12 13:17:51 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:2b7a32d7 · snapshot:pre-deploy-kkb-kn-in-2026-08-12_131750 · deployed
2026-08-12 13:17:51 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:b71865e2 · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-12_131751 · deployed
2026-08-12 13:17:52 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:179f8c07 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-12_131752 · deployed
2026-08-12 13:17:53 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:5eddfab4 · snapshot:pre-deploy-maya-hi-in-2026-08-12_131752 · deployed
2026-08-12 13:17:54 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:f7c78d28 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-12_131753 · deployed
2026-08-12 13:17:55 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:ace511ed · snapshot:pre-deploy-maya-hi-out-2026-08-12_131754 · deployed
2026-08-12 13:17:55 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:fc1b60fc · snapshot:pre-deploy-maya-hi-signals-2026-08-12_131755 · deployed
2026-08-12 13:44:15 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:43ebee75 · snapshot:pre-deploy-kkb-hi-signals-2026-08-12_134415 · deployed
2026-08-12 13:44:16 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:34325ed5 · snapshot:pre-deploy-kkb-kn-signals-2026-08-12_134416 · deployed
2026-08-12 13:44:17 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:5f93d046 · snapshot:pre-deploy-kkb-hi-out-2026-08-12_134416 · deployed
2026-08-12 13:44:17 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:97ed1749 · snapshot:pre-deploy-kkb-kn-out-2026-08-12_134417 · deployed
2026-08-12 13:44:18 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:9cf4c299 · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-12_134418 · deployed
2026-08-12 13:44:19 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:45cef811 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-12_134419 · deployed
2026-08-12 13:44:19 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:03ed5ef9 · snapshot:pre-deploy-maya-hi-in-2026-08-12_134419 · deployed
2026-08-12 13:44:20 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:f1b3f576 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-12_134420 · deployed
2026-08-12 13:44:21 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:af8ddbb0 · snapshot:pre-deploy-maya-hi-out-2026-08-12_134420 · deployed
2026-08-12 13:44:21 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:fe86be46 · snapshot:pre-deploy-maya-hi-signals-2026-08-12_134421 · deployed
2026-08-12 13:55:36 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:6e2a9318 · snapshot:pre-deploy-trrain-hi-out-2026-08-12_135536 · deployed
2026-08-12 13:55:37 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:9723fb22 · snapshot:pre-deploy-trrain-kn-out-2026-08-12_135537 · deployed
2026-08-12 13:55:37 · prod · trrain-hi-output · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Output.md · sha256:2f14669d · snapshot:pre-deploy-trrain-hi-output-2026-08-12_135537 · deployed
2026-08-12 13:55:38 · prod · trrain-kn-output · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Output.md · sha256:2f14669d · snapshot:pre-deploy-trrain-kn-output-2026-08-12_135538 · deployed
2026-08-12 13:55:38 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:bfa0b7b7 · snapshot:pre-deploy-maya-hi-out-2026-08-12_135538 · deployed
2026-08-12 13:55:39 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:10a17503 · snapshot:pre-deploy-maya-hi-signals-2026-08-12_135539 · deployed
2026-08-12 13:55:40 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:fb6ee5a8 · snapshot:pre-deploy-maya-hi-in-2026-08-12_135540 · deployed
2026-08-12 13:55:41 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:4ac104d1 · snapshot:pre-deploy-maya-hi-in-signals-2026-08-12_135540 · deployed
2026-08-12 14:02:23 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:63cb42b9 · snapshot:pre-deploy-trrain-kn-out-2026-08-12_140223 · deployed
2026-08-12 14:10:06 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:26797caa · snapshot:pre-deploy-kkb-hi-signals-2026-08-12_141006 · deployed
2026-08-12 14:10:07 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c169b283 · snapshot:pre-deploy-kkb-kn-signals-2026-08-12_141006 · deployed
2026-08-12 14:10:07 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:61c00568 · snapshot:pre-deploy-kkb-hi-out-2026-08-12_141007 · deployed
2026-08-12 14:10:08 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:f0066673 · snapshot:pre-deploy-kkb-kn-out-2026-08-12_141008 · deployed
2026-08-12 14:10:09 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:3032a71e · snapshot:pre-deploy-maya-hi-out-2026-08-12_141009 · deployed
2026-08-12 14:10:10 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:1965eaf3 · snapshot:pre-deploy-maya-hi-signals-2026-08-12_141009 · deployed
2026-08-12 14:10:10 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:37c02041 · snapshot:pre-deploy-kkb-hi-in-2026-08-12_141010 · deployed
2026-08-12 14:10:11 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:3ac4e478 · snapshot:pre-deploy-kkb-kn-in-2026-08-12_141011 · deployed
2026-08-12 14:44:21 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:d9be32d4 · snapshot:- · skip-in-sync
2026-08-12 14:44:23 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:39167bd4 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-12_144422 · deployed
2026-08-12 14:44:24 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:0d65a979 · snapshot:pre-deploy-maya-hi-in-2026-08-12_144423 · deployed
2026-08-12 14:44:26 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:934cd00f · snapshot:pre-deploy-maya-hi-in-signals-2026-08-12_144425 · deployed
2026-08-24 18:43:37 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:cf9dd519 · snapshot:pre-deploy-kkb-hi-out-2026-08-24_184336 · deployed
2026-08-24 18:43:37 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:38ceb10e · snapshot:pre-deploy-kkb-kn-out-2026-08-24_184337 · deployed
2026-08-24 18:43:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:c77bca02 · snapshot:pre-deploy-kkb-hi-signals-2026-08-24_184338 · deployed
2026-08-24 18:43:39 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:a4728527 · snapshot:pre-deploy-kkb-kn-signals-2026-08-24_184339 · deployed
2026-08-24 18:43:40 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:98bf8fa7 · snapshot:pre-deploy-kkb-hi-in-2026-08-24_184340 · deployed
2026-08-24 18:43:41 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:71a40e3e · snapshot:pre-deploy-kkb-kn-in-2026-08-24_184341 · deployed
2026-08-24 18:43:42 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:82b366e5 · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-24_184342 · deployed
2026-08-24 18:43:43 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:395886d0 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-24_184343 · deployed
2026-08-24 18:43:44 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:3c3242a4 · snapshot:pre-deploy-maya-hi-out-2026-08-24_184344 · deployed
2026-08-24 18:43:45 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:2c509d01 · snapshot:pre-deploy-maya-hi-signals-2026-08-24_184345 · deployed
2026-08-24 18:43:46 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:fc7aff82 · snapshot:pre-deploy-maya-hi-in-2026-08-24_184346 · deployed
2026-08-24 18:43:47 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:6447148b · snapshot:pre-deploy-maya-hi-in-signals-2026-08-24_184346 · deployed
2026-08-24 18:43:48 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:4d98a606 · snapshot:pre-deploy-trrain-kn-out-2026-08-24_184347 · deployed
2026-08-24 19:03:54 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:e887029a · snapshot:pre-deploy-kkb-hi-out-2026-08-24_190354 · deployed
2026-08-24 19:03:55 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:8555bb0b · snapshot:pre-deploy-kkb-kn-out-2026-08-24_190355 · deployed
2026-08-24 19:03:56 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5af723c7 · snapshot:pre-deploy-kkb-hi-in-2026-08-24_190356 · deployed
2026-08-24 19:03:57 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:768567c8 · snapshot:pre-deploy-kkb-kn-in-2026-08-24_190357 · deployed
2026-08-24 19:03:58 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:106e04eb · snapshot:pre-deploy-maya-hi-out-2026-08-24_190358 · deployed
2026-08-24 19:03:59 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:3a163625 · snapshot:pre-deploy-maya-hi-in-2026-08-24_190358 · deployed
2026-08-25 20:10:35 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:0025c5c7 · snapshot:pre-deploy-kkb-hi-out-2026-08-25_201035 · deployed
2026-08-25 20:10:36 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:ce334626 · snapshot:pre-deploy-kkb-kn-out-2026-08-25_201036 · deployed
2026-08-25 20:10:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:1660e733 · snapshot:pre-deploy-kkb-hi-signals-2026-08-25_201037 · deployed
2026-08-25 20:10:39 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:27b3c5ff · snapshot:pre-deploy-kkb-kn-signals-2026-08-25_201038 · deployed
2026-08-25 20:10:39 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:f4205ada · snapshot:pre-deploy-kkb-hi-in-2026-08-25_201039 · deployed
2026-08-25 20:10:40 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:f6796f0d · snapshot:pre-deploy-kkb-kn-in-2026-08-25_201040 · deployed
2026-08-25 20:10:46 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:beae02c5 · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-25_201045 · deployed
2026-08-25 20:10:47 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:967275cd · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-25_201047 · deployed
2026-08-25 20:10:49 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:cfc24f18 · snapshot:pre-deploy-maya-hi-out-2026-08-25_201048 · deployed
2026-08-25 20:10:50 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:6f68e01b · snapshot:pre-deploy-maya-hi-signals-2026-08-25_201049 · deployed
2026-08-25 20:10:51 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:8f4c9d35 · snapshot:pre-deploy-maya-hi-in-2026-08-25_201050 · deployed
2026-08-25 20:10:52 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:c4b02f9a · snapshot:pre-deploy-maya-hi-in-signals-2026-08-25_201051 · deployed
2026-08-25 20:28:28 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:aafe8ffe · snapshot:pre-deploy-kkb-hi-out-2026-08-25_202827 · deployed
2026-08-25 20:28:29 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:d10e9e0e · snapshot:pre-deploy-kkb-kn-out-2026-08-25_202828 · deployed
2026-08-25 20:28:29 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:b73fff01 · snapshot:pre-deploy-kkb-hi-signals-2026-08-25_202829 · deployed
2026-08-25 20:28:30 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:5512c0fd · snapshot:pre-deploy-kkb-kn-signals-2026-08-25_202830 · deployed
2026-08-25 20:28:31 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5a600f1b · snapshot:pre-deploy-kkb-hi-in-2026-08-25_202831 · deployed
2026-08-25 20:28:32 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:7ec849f9 · snapshot:pre-deploy-kkb-kn-in-2026-08-25_202831 · deployed
2026-08-25 20:28:33 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:df9a3758 · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-25_202832 · deployed
2026-08-25 20:28:34 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:cb700193 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-25_202833 · deployed
2026-08-25 20:28:35 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:1186b7d4 · snapshot:pre-deploy-maya-hi-out-2026-08-25_202834 · deployed
2026-08-25 20:28:36 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:20d46939 · snapshot:pre-deploy-maya-hi-signals-2026-08-25_202835 · deployed
2026-08-25 20:28:37 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:2539b454 · snapshot:pre-deploy-maya-hi-in-2026-08-25_202836 · deployed
2026-08-25 20:28:37 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:ce04672f · snapshot:pre-deploy-maya-hi-in-signals-2026-08-25_202837 · deployed
2026-08-28 12:33:30 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:224b1a67 · snapshot:pre-deploy-kkb-hi-in-signals-2026-08-28_123329 · deployed
2026-08-28 12:33:31 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:ac8fdf80 · snapshot:pre-deploy-kkb-kn-in-signals-2026-08-28_123330 · deployed
2026-08-28 12:33:32 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:566aa28a · snapshot:pre-deploy-maya-hi-in-signals-2026-08-28_123331 · deployed
2026-08-28 15:50:48 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:e4268729 · snapshot:pre-deploy-kkb-hi-signals-2026-08-28_155047 · deployed
2026-08-28 23:18:28 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:be672517 · snapshot:pre-deploy-kkb-hi-signals-2026-08-28_231827 · deployed
2026-08-28 23:52:40 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:84c42117 · snapshot:pre-deploy-kkb-hi-signals-2026-08-28_235239 · deployed
2026-08-31 15:07:46 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:87ea818c · snapshot:pre-deploy-kkb-hi-signals-2026-08-31_150745 · deployed
2026-08-31 17:28:06 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:94cdabe0 · snapshot:pre-deploy-kkb-hi-signals-2026-08-31_172805 · deployed
2026-08-31 18:06:34 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:4f310b99 · snapshot:pre-deploy-kkb-hi-signals-2026-08-31_180633 · deployed
2026-08-31 18:24:03 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:de5a5598 · snapshot:pre-deploy-kkb-hi-signals-2026-08-31_182403 · deployed
2026-08-31 18:55:46 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f152cf7a · snapshot:pre-deploy-kkb-hi-signals-2026-08-31_185546 · deployed
2026-08-31 19:46:45 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:b69e0912 · snapshot:pre-deploy-kkb-hi-signals-2026-08-31_194644 · deployed
2026-09-01 15:50:42 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:bb0e188d · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_155042 · deployed
2026-09-01 16:01:43 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:4a787302 · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_160141 · deployed
2026-09-01 16:02:57 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:24657c26 · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_160257 · deployed
2026-09-01 16:04:14 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:052cc20e · snapshot:pre-deploy-kkb-hi-out-2026-09-01_160414 · deployed
2026-09-01 16:04:15 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:af524c26 · snapshot:pre-deploy-kkb-kn-out-2026-09-01_160415 · deployed
2026-09-01 16:04:16 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:d2b17eea · snapshot:pre-deploy-kkb-hi-in-2026-09-01_160416 · deployed
2026-09-01 16:04:17 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:c664d8bf · snapshot:pre-deploy-kkb-kn-in-2026-09-01_160416 · deployed
2026-09-01 16:04:18 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:a38ceff7 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-01_160417 · deployed
2026-09-01 16:04:19 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:70605616 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-01_160418 · deployed
2026-09-01 16:04:20 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:bd1af75f · snapshot:pre-deploy-kkb-kn-signals-2026-09-01_160420 · deployed
2026-09-01 16:04:21 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:a6c8cdad · snapshot:pre-deploy-maya-hi-out-2026-09-01_160420 · deployed
2026-09-01 16:04:22 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:a8885bfe · snapshot:pre-deploy-maya-hi-signals-2026-09-01_160421 · deployed
2026-09-01 16:04:22 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:f0f6a078 · snapshot:pre-deploy-maya-hi-in-2026-09-01_160422 · deployed
2026-09-01 16:04:23 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:ea4c3f4b · snapshot:pre-deploy-maya-hi-in-signals-2026-09-01_160423 · deployed
2026-09-01 16:17:04 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:11b89504 · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_161703 · deployed
2026-09-01 16:17:05 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ef00413b · snapshot:pre-deploy-kkb-hi-out-2026-09-01_161705 · deployed
2026-09-01 16:17:08 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:5e60e761 · snapshot:pre-deploy-kkb-kn-out-2026-09-01_161707 · deployed
2026-09-01 16:17:09 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:b10a09d7 · snapshot:pre-deploy-kkb-hi-in-2026-09-01_161708 · deployed
2026-09-01 16:17:10 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:94d7305d · snapshot:pre-deploy-kkb-kn-in-2026-09-01_161709 · deployed
2026-09-01 16:17:10 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:2f97b8b7 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-01_161710 · deployed
2026-09-01 16:17:11 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:da68da22 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-01_161711 · deployed
2026-09-01 16:17:12 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:6814c91e · snapshot:pre-deploy-kkb-kn-signals-2026-09-01_161712 · deployed
2026-09-01 16:17:13 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:a3033e82 · snapshot:pre-deploy-maya-hi-out-2026-09-01_161713 · deployed
2026-09-01 16:17:14 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:89f08817 · snapshot:pre-deploy-maya-hi-signals-2026-09-01_161714 · deployed
2026-09-01 16:17:15 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:f8c460ea · snapshot:pre-deploy-maya-hi-in-2026-09-01_161715 · deployed
2026-09-01 16:17:16 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:e133490d · snapshot:pre-deploy-maya-hi-in-signals-2026-09-01_161716 · deployed
2026-09-01 16:27:08 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:2335856f · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_162707 · deployed
2026-09-01 16:31:00 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:43540170 · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_163059 · deployed
2026-09-01 16:47:58 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:6548caf0 · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_164757 · deployed
2026-09-01 17:10:02 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:59c3ef3c · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_171001 · deployed
2026-09-01 17:30:52 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f5ff8003 · snapshot:pre-deploy-kkb-hi-signals-2026-09-01_173051 · deployed
2026-09-02 09:58:17 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:6ddc02b9 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_095816 · deployed
2026-09-02 10:01:50 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:30a87a50 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_100149 · deployed
2026-09-02 10:01:51 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:442a2e42 · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_100150 · deployed
2026-09-02 10:01:52 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ddc47657 · snapshot:pre-deploy-kkb-hi-out-2026-09-02_100152 · deployed
2026-09-02 10:01:53 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:c6fb918b · snapshot:pre-deploy-kkb-kn-out-2026-09-02_100153 · deployed
2026-09-02 10:01:54 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:3763a63f · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-02_100154 · deployed
2026-09-02 10:01:55 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:2afd23bd · snapshot:pre-deploy-maya-hi-signals-2026-09-02_100155 · deployed
2026-09-02 10:01:56 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:ad46fd0e · snapshot:pre-deploy-maya-hi-out-2026-09-02_100156 · deployed
2026-09-02 10:01:57 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:d0ddf5dd · snapshot:pre-deploy-maya-hi-in-signals-2026-09-02_100157 · deployed
2026-09-02 10:01:59 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b6992476 · snapshot:pre-deploy-maya-hi-in-2026-09-02_100158 · deployed
2026-09-02 10:09:56 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:d7a3f577 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_100956 · deployed
2026-09-02 10:09:57 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:356db562 · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_100957 · deployed
2026-09-02 10:09:58 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:74a67463 · snapshot:pre-deploy-maya-hi-signals-2026-09-02_100957 · deployed
2026-09-02 10:09:59 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:7c87fae0 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-02_100958 · deployed
2026-09-02 10:59:00 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:3dce1565 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_105859 · deployed
2026-09-02 11:28:22 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:5951a449 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_112821 · deployed
2026-09-02 11:28:24 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:92a18097 · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_112823 · deployed
2026-09-02 11:28:27 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:a690201f · snapshot:pre-deploy-kkb-hi-out-2026-09-02_112826 · deployed
2026-09-02 11:28:31 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:82c6655f · snapshot:pre-deploy-kkb-kn-out-2026-09-02_112831 · deployed
2026-09-02 11:41:00 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:d1e887d8 · snapshot:pre-deploy-maya-hi-signals-2026-09-02_114058 · deployed
2026-09-02 11:41:02 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:f085544c · snapshot:pre-deploy-maya-hi-out-2026-09-02_114101 · deployed
2026-09-02 11:41:06 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:4bbf4750 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-02_114105 · deployed
2026-09-02 11:41:08 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:5054ebe0 · snapshot:pre-deploy-maya-hi-in-2026-09-02_114107 · deployed
2026-09-02 12:12:49 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:73221144 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_121248 · deployed
2026-09-02 12:12:51 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:2de9e8b6 · snapshot:pre-deploy-kkb-hi-out-2026-09-02_121250 · deployed
2026-09-02 12:12:53 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:89c4c755 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-02_121252 · deployed
2026-09-02 12:12:54 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:d1e887d8 · snapshot:- · skip-in-sync
2026-09-02 12:12:55 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:f085544c · snapshot:- · skip-in-sync
2026-09-02 12:12:56 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:4bbf4750 · snapshot:- · skip-in-sync
2026-09-02 12:12:58 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:5054ebe0 · snapshot:- · skip-in-sync
2026-09-02 15:38:19 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:ba81e108 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_153819 · deployed
2026-09-02 15:38:22 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:374fad6c · snapshot:pre-deploy-kkb-hi-out-2026-09-02_153821 · deployed
2026-09-02 15:38:23 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:3da77898 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-02_153822 · deployed
2026-09-02 16:35:21 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:cd4db0eb · snapshot:pre-deploy-maya-hi-signals-2026-09-02_163520 · deployed
2026-09-02 16:35:23 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:a54603f3 · snapshot:pre-deploy-maya-hi-out-2026-09-02_163523 · deployed
2026-09-02 16:35:24 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:02a38070 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-02_163524 · deployed
2026-09-02 16:35:25 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:5dfe3678 · snapshot:pre-deploy-maya-hi-in-2026-09-02_163525 · deployed
2026-09-02 16:39:37 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:e114b91d · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_163936 · deployed
2026-09-02 17:35:50 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:fc415e02 · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_173549 · deployed
2026-09-02 18:01:02 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:675f5ecb · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_180101 · deployed
2026-09-02 18:01:03 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1340cc77 · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_180102 · deployed
2026-09-02 18:01:03 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:3da77898 · snapshot:- · skip-in-sync
2026-09-02 18:01:04 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:da68da22 · snapshot:- · skip-in-sync
2026-09-02 18:01:04 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:cd4db0eb · snapshot:- · skip-in-sync
2026-09-02 18:01:05 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:02a38070 · snapshot:- · skip-in-sync
2026-09-02 18:02:28 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:675f5ecb · snapshot:- · skip-in-sync
2026-09-02 18:02:29 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1340cc77 · snapshot:- · skip-in-sync
2026-09-02 18:02:29 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:5a9bf09f · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-02_180229 · deployed
2026-09-02 18:02:30 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:4811a50b · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-02_180230 · deployed
2026-09-02 18:02:31 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:d46acecc · snapshot:pre-deploy-kkb-hi-in-2026-09-02_180231 · deployed
2026-09-02 18:02:33 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:1e8e761f · snapshot:pre-deploy-kkb-kn-in-2026-09-02_180232 · deployed
2026-09-02 18:02:34 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:dfb14e79 · snapshot:pre-deploy-maya-hi-signals-2026-09-02_180234 · deployed
2026-09-02 18:02:35 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:f5201055 · snapshot:pre-deploy-maya-hi-out-2026-09-02_180235 · deployed
2026-09-02 18:02:36 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:96c043bd · snapshot:pre-deploy-maya-hi-in-signals-2026-09-02_180236 · deployed
2026-09-02 18:02:37 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:c3e52427 · snapshot:pre-deploy-maya-hi-in-2026-09-02_180237 · deployed
2026-09-02 18:07:22 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:aec5e097 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_180721 · deployed
2026-09-02 18:07:23 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:56438ca6 · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_180722 · deployed
2026-09-02 18:07:24 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:57db0d5a · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-02_180723 · deployed
2026-09-02 18:07:24 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:0b064ecf · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-02_180724 · deployed
2026-09-02 18:07:25 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:36732456 · snapshot:pre-deploy-kkb-hi-in-2026-09-02_180725 · deployed
2026-09-02 18:07:27 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:69bdce0d · snapshot:pre-deploy-kkb-kn-in-2026-09-02_180726 · deployed
2026-09-02 18:07:28 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:bfc95c8f · snapshot:pre-deploy-maya-hi-in-signals-2026-09-02_180727 · deployed
2026-09-02 18:07:29 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:c5bccb82 · snapshot:pre-deploy-maya-hi-in-2026-09-02_180728 · deployed
2026-09-02 18:08:06 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:53510201 · snapshot:pre-deploy-kkb-hi-in-2026-09-02_180806 · deployed
2026-09-02 18:08:07 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:0f97bfcf · snapshot:pre-deploy-kkb-kn-in-2026-09-02_180806 · deployed
2026-09-02 18:08:08 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:f32bc203 · snapshot:pre-deploy-maya-hi-in-2026-09-02_180808 · deployed
2026-09-02 18:08:38 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:a437b267 · snapshot:pre-deploy-kkb-hi-in-2026-09-02_180838 · deployed
2026-09-02 18:08:39 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:72e42299 · snapshot:pre-deploy-kkb-kn-in-2026-09-02_180839 · deployed
2026-09-02 18:08:40 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:9d804992 · snapshot:pre-deploy-maya-hi-in-2026-09-02_180840 · deployed
2026-09-02 18:09:31 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:af9d5310 · snapshot:pre-deploy-kkb-hi-signals-2026-09-02_180930 · deployed
2026-09-02 18:09:32 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:e2e5a5bd · snapshot:pre-deploy-kkb-kn-signals-2026-09-02_180931 · deployed
2026-09-03 02:52:15 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:df8f6d7e · snapshot:pre-deploy-dkb-hi-signals-2026-09-03_025214 · deployed
2026-09-03 02:52:17 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:0ae408fb · snapshot:- · skip-in-sync
2026-09-03 02:54:01 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:8d241294 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_025400 · deployed
2026-09-03 02:55:01 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:c3a438bb · snapshot:pre-deploy-dkb-kn-signals-2026-09-03_025501 · deployed
2026-09-03 02:55:02 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:5c5d50c4 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_025502 · deployed
2026-09-03 02:55:05 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:c3e63321 · snapshot:pre-deploy-maya-hi-out-2026-09-03_025504 · deployed
2026-09-03 02:55:05 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:bfc95c8f · snapshot:- · skip-in-sync
2026-09-03 02:55:06 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:9d804992 · snapshot:- · skip-in-sync
2026-09-03 03:36:23 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:e94dbce4 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_033622 · deployed
2026-09-03 03:37:07 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:b421f35c · snapshot:pre-deploy-dkb-hi-signals-2026-09-03_033706 · deployed
2026-09-03 03:37:08 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:d6a566ef · snapshot:pre-deploy-dkb-kn-signals-2026-09-03_033707 · deployed
2026-09-03 04:01:45 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:054d9301 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_040144 · deployed
2026-09-03 04:01:46 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:03c7fee7 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_040145 · deployed
2026-09-03 04:13:49 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:228f4cfa · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_041349 · deployed
2026-09-03 04:13:50 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:4e3850f5 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_041350 · deployed
2026-09-03 04:15:19 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:2298b404 · snapshot:pre-deploy-dkb-kn-signals-2026-09-03_041519 · deployed
2026-09-03 05:18:54 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:4f0f2869 · snapshot:pre-deploy-dkb-hi-signals-2026-09-03_051853 · deployed
2026-09-03 05:27:20 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:e13de313 · snapshot:pre-deploy-dkb-hi-signals-2026-09-03_052719 · deployed
2026-09-03 05:27:21 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:0b6e207c · snapshot:pre-deploy-dkb-kn-signals-2026-09-03_052720 · deployed
2026-09-03 05:39:44 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:420b4ded · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_053944 · deployed
2026-09-03 05:39:45 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:08e2ce87 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_053945 · deployed
2026-09-03 06:11:36 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:bc92d058 · snapshot:pre-deploy-dkb-hi-signals-2026-09-03_061136 · deployed
2026-09-03 06:11:37 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:36ee9787 · snapshot:pre-deploy-dkb-kn-signals-2026-09-03_061137 · deployed
2026-09-03 06:12:11 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f2e165b8 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_061210 · deployed
2026-09-03 06:12:12 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:b3914845 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_061211 · deployed
2026-09-03 06:12:13 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:278a8080 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_061213 · deployed
2026-09-03 06:12:14 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:3d8a87fa · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_061213 · deployed
2026-09-03 06:12:14 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:04334b91 · snapshot:pre-deploy-kkb-hi-out-2026-09-03_061214 · deployed
2026-09-03 06:12:15 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:96043383 · snapshot:pre-deploy-kkb-kn-out-2026-09-03_061215 · deployed
2026-09-03 06:12:16 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:14b601f7 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_061216 · deployed
2026-09-03 06:12:17 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:de85457d · snapshot:pre-deploy-kkb-kn-in-2026-09-03_061216 · deployed
2026-09-03 06:12:18 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:b5abc0cd · snapshot:pre-deploy-maya-hi-signals-2026-09-03_061217 · deployed
2026-09-03 06:12:18 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:6b123257 · snapshot:pre-deploy-maya-hi-out-2026-09-03_061218 · deployed
2026-09-03 06:12:19 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:86319ae0 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_061219 · deployed
2026-09-03 06:12:20 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:17f98a35 · snapshot:pre-deploy-maya-hi-in-2026-09-03_061219 · deployed
2026-09-03 06:26:17 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:260c30cd · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_062616 · deployed
2026-09-03 06:26:18 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:8758b3fe · snapshot:pre-deploy-kkb-hi-out-2026-09-03_062617 · deployed
2026-09-03 06:26:19 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:f741dd49 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_062618 · deployed
2026-09-03 06:26:20 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:447bc842 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_062620 · deployed
2026-09-03 06:26:46 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:34aedc40 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_062645 · deployed
2026-09-03 06:26:46 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:3d8a87fa · snapshot:- · skip-in-sync
2026-09-03 06:26:47 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:96043383 · snapshot:- · skip-in-sync
2026-09-03 06:26:47 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:de85457d · snapshot:- · skip-in-sync
2026-09-03 10:09:02 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:74a47b2d · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_100902 · deployed
2026-09-03 10:09:05 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:cae20b1f · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_100904 · deployed
2026-09-03 10:09:05 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:fa86fae5 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_100905 · deployed
2026-09-03 10:09:06 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:d397b0fc · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_100906 · deployed
2026-09-03 10:09:08 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:931fe42c · snapshot:pre-deploy-kkb-hi-out-2026-09-03_100907 · deployed
2026-09-03 10:09:09 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:fa6bd58a · snapshot:pre-deploy-kkb-kn-out-2026-09-03_100909 · deployed
2026-09-03 10:09:10 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:ff8cf48d · snapshot:pre-deploy-kkb-hi-in-2026-09-03_100910 · deployed
2026-09-03 10:09:11 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:a7f9989c · snapshot:pre-deploy-kkb-kn-in-2026-09-03_100911 · deployed
2026-09-03 10:09:12 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:b8d6830c · snapshot:pre-deploy-maya-hi-signals-2026-09-03_100912 · deployed
2026-09-03 10:09:13 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:6e112f8f · snapshot:pre-deploy-maya-hi-out-2026-09-03_100913 · deployed
2026-09-03 10:09:14 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:f16e3b85 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_100914 · deployed
2026-09-03 10:09:15 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:6a299bda · snapshot:pre-deploy-maya-hi-in-2026-09-03_100915 · deployed
2026-09-03 10:33:29 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:24a7579d · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_103326 · deployed
2026-09-03 10:33:33 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:6a1d2f95 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_103330 · deployed
2026-09-03 10:33:37 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:fbfc323f · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_103335 · deployed
2026-09-03 10:33:39 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:1b413364 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_103338 · deployed
2026-09-03 10:33:42 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:384248ee · snapshot:pre-deploy-kkb-hi-out-2026-09-03_103341 · deployed
2026-09-03 10:33:44 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:fa6bd58a · snapshot:- · skip-in-sync
2026-09-03 10:33:47 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:7863b67b · snapshot:pre-deploy-kkb-hi-in-2026-09-03_103345 · deployed
2026-09-03 10:33:48 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:a7f9989c · snapshot:- · skip-in-sync
2026-09-03 10:33:52 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:5d8f21a8 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_103350 · deployed
2026-09-03 10:33:55 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:07358eb2 · snapshot:pre-deploy-maya-hi-out-2026-09-03_103354 · deployed
2026-09-03 10:33:59 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:b9dd986d · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_103357 · deployed
2026-09-03 10:34:02 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:07633f3c · snapshot:pre-deploy-maya-hi-in-2026-09-03_103400 · deployed
2026-09-03 11:07:25 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f80d42a6 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_110722 · deployed
2026-09-03 11:12:19 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:24a7579d · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_111217 · deployed
2026-09-03 12:05:15 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:43e07335 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_120513 · deployed
2026-09-03 12:05:23 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:2b5c7038 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_120517 · deployed
2026-09-03 12:05:28 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:12ee4754 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_120525 · deployed
2026-09-03 12:05:34 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:48d79dfe · snapshot:pre-deploy-kkb-kn-in-2026-09-03_120530 · deployed
2026-09-03 12:38:10 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:bd3134d7 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_123808 · deployed
2026-09-03 12:38:13 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:94382f81 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_123811 · deployed
2026-09-03 12:38:17 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:d617f552 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_123815 · deployed
2026-09-03 12:38:18 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:384248ee · snapshot:- · skip-in-sync
2026-09-03 12:38:20 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:fa6bd58a · snapshot:- · skip-in-sync
2026-09-03 12:38:23 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:d6c21779 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_123822 · deployed
2026-09-03 12:38:26 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:46eec2b3 · snapshot:pre-deploy-kkb-kn-in-2026-09-03_123825 · deployed
2026-09-03 12:38:29 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:378264fd · snapshot:pre-deploy-maya-hi-signals-2026-09-03_123828 · deployed
2026-09-03 12:38:32 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:852e0090 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_123831 · deployed
2026-09-03 12:38:49 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:b0098194 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_123848 · deployed
2026-09-03 12:51:36 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:b16abef4 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_125134 · deployed
2026-09-03 12:52:52 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:39c9043c · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_125251 · deployed
2026-09-03 13:00:49 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:53a98c67 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_130046 · deployed
2026-09-03 13:00:52 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:bbebd5a5 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_130050 · deployed
2026-09-03 13:23:33 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:6b6b7b1c · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_132333 · deployed
2026-09-03 13:23:34 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:a10526e2 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_132334 · deployed
2026-09-03 13:23:35 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:6e19dce3 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_132335 · deployed
2026-09-03 13:23:36 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:f4a61af2 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_132336 · deployed
2026-09-03 13:23:37 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:0092e19a · snapshot:pre-deploy-kkb-hi-out-2026-09-03_132337 · deployed
2026-09-03 13:23:38 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:d6ebbf6d · snapshot:pre-deploy-kkb-kn-out-2026-09-03_132337 · deployed
2026-09-03 13:23:39 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:a980a8f6 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_132339 · deployed
2026-09-03 13:23:40 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:aa659690 · snapshot:pre-deploy-kkb-kn-in-2026-09-03_132339 · deployed
2026-09-03 13:23:41 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:7156f0c2 · snapshot:pre-deploy-maya-hi-out-2026-09-03_132340 · deployed
2026-09-03 13:23:41 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:a08b7453 · snapshot:pre-deploy-maya-hi-in-2026-09-03_132341 · deployed
2026-09-03 13:28:25 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:6f2f838e · snapshot:pre-deploy-dkb-hi-signals-2026-09-03_132825 · deployed
2026-09-03 13:52:24 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:0de5e8ae · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_135223 · deployed
2026-09-03 13:52:25 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:8baf15d6 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_135224 · deployed
2026-09-03 13:52:26 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:2f086acc · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_135225 · deployed
2026-09-03 13:52:26 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:3ed8fdff · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_135226 · deployed
2026-09-03 13:52:27 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:349187ab · snapshot:pre-deploy-maya-hi-signals-2026-09-03_135227 · deployed
2026-09-03 13:52:28 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:a4a999a1 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_135228 · deployed
2026-09-03 13:52:29 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:8c362c90 · snapshot:pre-deploy-kkb-hi-out-2026-09-03_135229 · deployed
2026-09-03 13:52:30 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:9548ff2d · snapshot:pre-deploy-kkb-kn-out-2026-09-03_135229 · deployed
2026-09-03 13:52:31 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:41cfcbb0 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_135230 · deployed
2026-09-03 13:52:32 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:5460abce · snapshot:pre-deploy-kkb-kn-in-2026-09-03_135231 · deployed
2026-09-03 13:52:32 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:5e564a44 · snapshot:pre-deploy-maya-hi-out-2026-09-03_135232 · deployed
2026-09-03 13:52:34 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:a5e88e31 · snapshot:pre-deploy-maya-hi-in-2026-09-03_135233 · deployed
2026-09-03 14:00:28 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:a32dafb1 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_140028 · deployed
2026-09-03 14:00:30 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:b43f7f52 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_140030 · deployed
2026-09-03 14:00:35 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:04a84d62 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_140032 · deployed
2026-09-03 14:00:41 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:e8c97ab6 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_140037 · deployed
2026-09-03 14:00:45 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:e1590fe8 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_140043 · deployed
2026-09-03 14:00:49 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:3bb5742d · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_140047 · deployed
2026-09-03 14:00:54 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ca630e4a · snapshot:pre-deploy-kkb-hi-out-2026-09-03_140052 · deployed
2026-09-03 14:00:58 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:89ea2d34 · snapshot:pre-deploy-kkb-kn-out-2026-09-03_140056 · deployed
2026-09-03 14:01:03 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:2066ee4f · snapshot:pre-deploy-kkb-hi-in-2026-09-03_140100 · deployed
2026-09-03 14:01:07 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:396670e7 · snapshot:pre-deploy-kkb-kn-in-2026-09-03_140105 · deployed
2026-09-03 14:01:12 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:c645360f · snapshot:pre-deploy-maya-hi-out-2026-09-03_140109 · deployed
2026-09-03 14:01:16 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b71efe57 · snapshot:pre-deploy-maya-hi-in-2026-09-03_140114 · deployed
2026-09-03 14:11:36 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:a12f17ac · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_141132 · deployed
2026-09-03 14:20:27 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:ed8f60d3 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_142026 · deployed
2026-09-03 14:20:30 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:84373e0a · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_142028 · deployed
2026-09-03 14:20:32 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:eaaea42b · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_142032 · deployed
2026-09-03 14:20:34 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:22df6095 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_142033 · deployed
2026-09-03 14:20:36 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:839da6d7 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_142036 · deployed
2026-09-03 14:20:39 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:f3b6652a · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_142037 · deployed
2026-09-03 14:20:42 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:36c07565 · snapshot:pre-deploy-kkb-hi-out-2026-09-03_142040 · deployed
2026-09-03 14:20:44 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:90ebc061 · snapshot:pre-deploy-kkb-kn-out-2026-09-03_142043 · deployed
2026-09-03 14:20:47 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:11f20609 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_142046 · deployed
2026-09-03 14:20:50 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:53dcd19c · snapshot:pre-deploy-kkb-kn-in-2026-09-03_142048 · deployed
2026-09-03 14:20:52 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:22ff2ce5 · snapshot:pre-deploy-maya-hi-out-2026-09-03_142051 · deployed
2026-09-03 14:20:55 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:e2e2323f · snapshot:pre-deploy-maya-hi-in-2026-09-03_142054 · deployed
2026-09-03 14:32:36 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:17a6bb87 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_143236 · deployed
2026-09-03 14:32:37 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c2153ed1 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_143237 · deployed
2026-09-03 14:32:38 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:942fa317 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_143238 · deployed
2026-09-03 14:32:39 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:4ee01cba · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_143239 · deployed
2026-09-03 14:32:40 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:4f1fbc45 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_143240 · deployed
2026-09-03 14:32:41 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:9588e186 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_143241 · deployed
2026-09-03 14:32:42 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:6a47c7bf · snapshot:pre-deploy-kkb-hi-out-2026-09-03_143242 · deployed
2026-09-03 14:32:43 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:7240b21f · snapshot:pre-deploy-kkb-kn-out-2026-09-03_143243 · deployed
2026-09-03 14:32:44 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:777debbb · snapshot:pre-deploy-kkb-hi-in-2026-09-03_143244 · deployed
2026-09-03 14:32:45 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:838a59fd · snapshot:pre-deploy-kkb-kn-in-2026-09-03_143245 · deployed
2026-09-03 14:32:46 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:36458437 · snapshot:pre-deploy-maya-hi-out-2026-09-03_143245 · deployed
2026-09-03 14:32:47 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:ee796b13 · snapshot:pre-deploy-maya-hi-in-2026-09-03_143246 · deployed
2026-09-03 14:44:32 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:ca137dfd · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_144432 · deployed
2026-09-03 14:44:33 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:14adcfe4 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_144433 · deployed
2026-09-03 14:44:34 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:fa621847 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_144434 · deployed
2026-09-03 14:44:35 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:34187e1d · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_144435 · deployed
2026-09-03 14:44:36 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:6fe43e9a · snapshot:pre-deploy-maya-hi-signals-2026-09-03_144436 · deployed
2026-09-03 14:44:37 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:d1d1e3b7 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_144437 · deployed
2026-09-03 14:44:38 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:60b1dac6 · snapshot:pre-deploy-kkb-hi-out-2026-09-03_144438 · deployed
2026-09-03 14:44:39 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:7308fe62 · snapshot:pre-deploy-kkb-kn-out-2026-09-03_144439 · deployed
2026-09-03 14:44:40 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:d0388a09 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_144440 · deployed
2026-09-03 14:44:41 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:91082919 · snapshot:pre-deploy-kkb-kn-in-2026-09-03_144441 · deployed
2026-09-03 14:44:42 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:f5936c7d · snapshot:pre-deploy-maya-hi-out-2026-09-03_144442 · deployed
2026-09-03 14:44:43 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:0e9328a2 · snapshot:pre-deploy-maya-hi-in-2026-09-03_144442 · deployed
2026-09-03 14:56:11 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:8e6cfc31 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_145610 · deployed
2026-09-03 14:56:12 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:3fb73362 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_145611 · deployed
2026-09-03 14:56:13 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:9107ce52 · snapshot:pre-deploy-kkb-hi-out-2026-09-03_145613 · deployed
2026-09-03 14:56:14 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:1692d2eb · snapshot:pre-deploy-kkb-kn-out-2026-09-03_145614 · deployed
2026-09-03 15:29:31 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:601fa785 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_152930 · deployed
2026-09-03 15:29:35 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:e9d0f431 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_152933 · deployed
2026-09-03 15:29:39 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:ee0e4e90 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_152937 · deployed
2026-09-03 15:29:43 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:72505a4e · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_152941 · deployed
2026-09-03 15:29:47 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:8805e2af · snapshot:pre-deploy-maya-hi-signals-2026-09-03_152945 · deployed
2026-09-03 15:29:51 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:e20b2449 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_152949 · deployed
2026-09-03 15:29:54 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:807301eb · snapshot:pre-deploy-kkb-hi-out-2026-09-03_152952 · deployed
2026-09-03 15:29:57 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:a13ae108 · snapshot:pre-deploy-kkb-kn-out-2026-09-03_152956 · deployed
2026-09-03 15:30:01 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:6628abf9 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_152959 · deployed
2026-09-03 15:30:04 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:f5d39412 · snapshot:pre-deploy-kkb-kn-in-2026-09-03_153002 · deployed
2026-09-03 15:30:08 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:adcb40b5 · snapshot:pre-deploy-maya-hi-out-2026-09-03_153006 · deployed
2026-09-03 15:30:11 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:7247a8b6 · snapshot:pre-deploy-maya-hi-in-2026-09-03_153009 · deployed
2026-09-03 15:37:41 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:691b463e · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_153740 · deployed
2026-09-03 16:39:15 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:a039361c · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_163912 · deployed
2026-09-03 16:39:19 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:6138bb3e · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_163918 · deployed
2026-09-03 16:39:22 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:4dcf507a · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_163920 · deployed
2026-09-03 16:39:27 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:c32a2ae4 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_163923 · deployed
2026-09-03 16:39:30 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:c5777d2e · snapshot:pre-deploy-maya-hi-signals-2026-09-03_163929 · deployed
2026-09-03 16:39:31 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:84d2b8bb · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_163930 · deployed
2026-09-03 16:39:35 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:95010283 · snapshot:pre-deploy-kkb-hi-out-2026-09-03_163932 · deployed
2026-09-03 16:39:36 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:31f53dd6 · snapshot:pre-deploy-kkb-kn-out-2026-09-03_163935 · deployed
2026-09-03 16:39:40 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:ec62bbde · snapshot:pre-deploy-kkb-hi-in-2026-09-03_163937 · deployed
2026-09-03 16:39:42 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:99701c3a · snapshot:pre-deploy-kkb-kn-in-2026-09-03_163941 · deployed
2026-09-03 16:39:42 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e722cdb1 · snapshot:pre-deploy-maya-hi-out-2026-09-03_163942 · deployed
2026-09-03 16:39:43 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:1e39063c · snapshot:pre-deploy-maya-hi-in-2026-09-03_163943 · deployed
2026-09-03 17:10:41 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:4734a414 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_171040 · deployed
2026-09-03 17:10:42 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:84627c6a · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_171041 · deployed
2026-09-03 17:10:43 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:f90fa387 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_171042 · deployed
2026-09-03 17:10:44 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:30203ea9 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_171043 · deployed
2026-09-03 17:10:45 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7075b056 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_171044 · deployed
2026-09-03 17:10:46 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:cf79b88a · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_171045 · deployed
2026-09-03 17:10:47 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:6f79754f · snapshot:pre-deploy-kkb-hi-out-2026-09-03_171046 · deployed
2026-09-03 17:10:48 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:0eb3c4dd · snapshot:pre-deploy-kkb-kn-out-2026-09-03_171048 · deployed
2026-09-03 17:10:49 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:6602bd65 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_171049 · deployed
2026-09-03 17:10:50 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:96410b7a · snapshot:pre-deploy-kkb-kn-in-2026-09-03_171050 · deployed
2026-09-03 17:10:51 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:154d310c · snapshot:pre-deploy-maya-hi-out-2026-09-03_171051 · deployed
2026-09-03 17:10:52 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:a1f607ff · snapshot:pre-deploy-maya-hi-in-2026-09-03_171052 · deployed
2026-09-03 17:52:18 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:5d3ce37f · snapshot:pre-deploy-maya-hi-signals-2026-09-03_175217 · deployed
2026-09-03 17:52:19 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:47cc3ae4 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_175218 · deployed
2026-09-03 17:52:20 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b2f84985 · snapshot:pre-deploy-maya-hi-out-2026-09-03_175220 · deployed
2026-09-03 17:52:21 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:6d43cdaf · snapshot:pre-deploy-maya-hi-in-2026-09-03_175221 · deployed
2026-09-03 17:52:22 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:5ad84e14 · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_175222 · deployed
2026-09-03 17:52:23 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:528e9838 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_175223 · deployed
2026-09-03 17:52:24 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:128572a2 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_175224 · deployed
2026-09-03 17:52:26 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:2459b914 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_175225 · deployed
2026-09-03 17:52:27 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:94d0f11e · snapshot:pre-deploy-kkb-hi-out-2026-09-03_175226 · deployed
2026-09-03 17:52:28 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2f7e3f9e · snapshot:pre-deploy-kkb-kn-out-2026-09-03_175228 · deployed
2026-09-03 17:52:30 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:0f8deda0 · snapshot:pre-deploy-kkb-hi-in-2026-09-03_175229 · deployed
2026-09-03 17:52:31 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:3c5e9137 · snapshot:pre-deploy-kkb-kn-in-2026-09-03_175230 · deployed
2026-09-03 18:56:24 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:7392bdba · snapshot:pre-deploy-kkb-hi-signals-2026-09-03_185622 · deployed
2026-09-03 18:56:25 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:61325c79 · snapshot:pre-deploy-kkb-kn-signals-2026-09-03_185624 · deployed
2026-09-03 18:56:28 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:8976599e · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-03_185626 · deployed
2026-09-03 18:56:29 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:c48f89ed · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-03_185629 · deployed
2026-09-03 18:56:33 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:4e3e7fb9 · snapshot:pre-deploy-maya-hi-signals-2026-09-03_185631 · deployed
2026-09-03 18:56:36 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:782f7788 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-03_185634 · deployed
2026-09-04 11:51:24 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:9ebf0708 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_115123 · deployed
2026-09-04 11:51:26 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:b1756d30 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_115125 · deployed
2026-09-04 11:51:27 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:09bb69ba · snapshot:pre-deploy-kkb-hi-in-2026-09-04_115127 · deployed
2026-09-04 11:51:29 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:5f997119 · snapshot:pre-deploy-kkb-kn-in-2026-09-04_115128 · deployed
2026-09-04 11:51:30 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:95f98b08 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_115129 · deployed
2026-09-04 11:51:31 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:42757bd4 · snapshot:pre-deploy-maya-hi-in-2026-09-04_115131 · deployed
2026-09-04 12:07:07 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:46a102a4 · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_120706 · deployed
2026-09-04 12:07:08 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1b004125 · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_120707 · deployed
2026-09-04 12:07:09 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:50cf696b · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_120708 · deployed
2026-09-04 12:07:10 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:aa3b6942 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_120709 · deployed
2026-09-04 12:07:11 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7488f52e · snapshot:pre-deploy-maya-hi-signals-2026-09-04_120710 · deployed
2026-09-04 12:07:12 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:bb15a417 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_120712 · deployed
2026-09-04 14:12:59 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:33da8eac · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_141259 · deployed
2026-09-04 14:13:02 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:d4d13f1c · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_141300 · deployed
2026-09-04 14:13:03 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:3db83277 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_141302 · deployed
2026-09-04 14:13:04 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:69b6df8a · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_141304 · deployed
2026-09-04 14:13:05 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7488f52e · snapshot:- · skip-in-sync
2026-09-04 14:13:06 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:bb15a417 · snapshot:- · skip-in-sync
2026-09-04 14:13:16 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7488f52e · snapshot:- · skip-in-sync
2026-09-04 14:13:36 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7488f52e · snapshot:- · skip-in-sync
2026-09-04 14:13:37 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:bb15a417 · snapshot:- · skip-in-sync
2026-09-04 14:13:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:33da8eac · snapshot:- · skip-in-sync
2026-09-04 14:13:39 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:d4d13f1c · snapshot:- · skip-in-sync
2026-09-04 14:13:39 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:3db83277 · snapshot:- · skip-in-sync
2026-09-04 14:13:40 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:69b6df8a · snapshot:- · skip-in-sync
2026-09-04 14:14:17 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:a3ac55f6 · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_141416 · deployed
2026-09-04 20:13:23 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:90169fa7 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_201322 · deployed
2026-09-04 20:13:24 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:a0df0e3c · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_201323 · deployed
2026-09-04 20:13:25 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:1d7c134f · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_201324 · deployed
2026-09-04 20:13:26 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:0b28e69b · snapshot:pre-deploy-kkb-hi-in-2026-09-04_201325 · deployed
2026-09-04 20:13:27 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:4a758aca · snapshot:pre-deploy-kkb-kn-in-2026-09-04_201327 · deployed
2026-09-04 20:13:28 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:ff81f5e1 · snapshot:pre-deploy-maya-hi-in-2026-09-04_201328 · deployed
2026-09-04 20:19:27 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:9cdc3537 · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_201926 · deployed
2026-09-04 20:19:28 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c90dfbe4 · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_201928 · deployed
2026-09-04 20:19:30 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:0108d1b3 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_201929 · deployed
2026-09-04 20:19:31 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:211376eb · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_201930 · deployed
2026-09-04 20:19:33 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:37182e20 · snapshot:pre-deploy-maya-hi-signals-2026-09-04_201932 · deployed
2026-09-04 20:19:34 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:af31d4e6 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_201933 · deployed
2026-09-04 20:19:37 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:265eed53 · snapshot:pre-deploy-kkb-hi-out-2026-09-04_201935 · deployed
2026-09-04 20:19:39 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:946b0c22 · snapshot:pre-deploy-kkb-kn-out-2026-09-04_201938 · deployed
2026-09-04 20:19:39 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:d1f5b0f1 · snapshot:pre-deploy-kkb-hi-in-2026-09-04_201939 · deployed
2026-09-04 20:19:41 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:9212e570 · snapshot:pre-deploy-kkb-kn-in-2026-09-04_201940 · deployed
2026-09-04 20:19:42 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:ffed2a3f · snapshot:pre-deploy-maya-hi-out-2026-09-04_201941 · deployed
2026-09-04 20:19:43 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b9f93d2e · snapshot:pre-deploy-maya-hi-in-2026-09-04_201943 · deployed
2026-09-04 20:23:44 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:6eae7106 · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_202343 · deployed
2026-09-04 20:23:45 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:d56fa399 · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_202344 · deployed
2026-09-04 20:23:46 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:15ff2dfa · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_202345 · deployed
2026-09-04 20:23:47 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:91e49082 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_202346 · deployed
2026-09-04 20:23:48 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:caa8b5f2 · snapshot:pre-deploy-maya-hi-signals-2026-09-04_202347 · deployed
2026-09-04 20:23:49 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:18deac53 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_202349 · deployed
2026-09-04 20:23:50 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:6f306234 · snapshot:pre-deploy-kkb-hi-out-2026-09-04_202350 · deployed
2026-09-04 20:23:52 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:47a82242 · snapshot:pre-deploy-kkb-kn-out-2026-09-04_202351 · deployed
2026-09-04 20:23:53 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:443430a4 · snapshot:pre-deploy-kkb-hi-in-2026-09-04_202352 · deployed
2026-09-04 20:23:55 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:59aa4ed0 · snapshot:pre-deploy-kkb-kn-in-2026-09-04_202354 · deployed
2026-09-04 20:23:56 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:c5f69970 · snapshot:pre-deploy-maya-hi-out-2026-09-04_202355 · deployed
2026-09-04 20:23:58 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b2cb029d · snapshot:pre-deploy-maya-hi-in-2026-09-04_202357 · deployed
2026-09-04 20:43:49 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:81cc2887 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_204349 · deployed
2026-09-04 20:43:51 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:a6f08e81 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_204350 · deployed
2026-09-04 20:43:52 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:a479be74 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_204351 · deployed
2026-09-04 20:43:53 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:d612f387 · snapshot:pre-deploy-kkb-hi-in-2026-09-04_204353 · deployed
2026-09-04 20:43:55 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:ef957c1e · snapshot:pre-deploy-kkb-kn-in-2026-09-04_204354 · deployed
2026-09-04 20:43:58 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:92fc554b · snapshot:pre-deploy-maya-hi-in-2026-09-04_204357 · deployed
2026-09-04 20:52:54 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:33da8eac · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_205253 · deployed
2026-09-04 20:52:56 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:a3ac55f6 · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_205255 · deployed
2026-09-04 20:52:58 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:e879d91d · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_205257 · deployed
2026-09-04 20:53:00 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:bf40e5b9 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_205300 · deployed
2026-09-04 20:53:02 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7488f52e · snapshot:pre-deploy-maya-hi-signals-2026-09-04_205301 · deployed
2026-09-04 20:53:04 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:5b057a2d · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_205303 · deployed
2026-09-04 20:53:07 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:94d0f11e · snapshot:pre-deploy-kkb-hi-out-2026-09-04_205307 · deployed
2026-09-04 20:53:11 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2f7e3f9e · snapshot:pre-deploy-kkb-kn-out-2026-09-04_205310 · deployed
2026-09-04 20:53:12 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:e10ee4c8 · snapshot:pre-deploy-kkb-hi-in-2026-09-04_205311 · deployed
2026-09-04 20:53:13 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:764fa820 · snapshot:pre-deploy-kkb-kn-in-2026-09-04_205312 · deployed
2026-09-04 20:53:14 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b2f84985 · snapshot:pre-deploy-maya-hi-out-2026-09-04_205314 · deployed
2026-09-04 20:53:15 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:eae40673 · snapshot:pre-deploy-maya-hi-in-2026-09-04_205315 · deployed
2026-09-04 21:13:39 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:5a42ac51 · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_211339 · deployed
2026-09-04 21:13:41 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:d3359656 · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_211340 · deployed
2026-09-04 21:13:42 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:0ec2caef · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-04_211341 · deployed
2026-09-04 21:13:43 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:b344ae08 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-04_211342 · deployed
2026-09-04 21:13:44 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:02b94f70 · snapshot:pre-deploy-maya-hi-signals-2026-09-04_211344 · deployed
2026-09-04 21:13:46 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:fd9e4bd6 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_211345 · deployed
2026-09-04 21:13:47 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:40757263 · snapshot:pre-deploy-kkb-hi-out-2026-09-04_211346 · deployed
2026-09-04 21:13:49 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:56d54ff3 · snapshot:pre-deploy-kkb-kn-out-2026-09-04_211348 · deployed
2026-09-04 21:13:50 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:e6ceab98 · snapshot:pre-deploy-kkb-hi-in-2026-09-04_211349 · deployed
2026-09-04 21:13:53 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:e455128c · snapshot:pre-deploy-kkb-kn-in-2026-09-04_211352 · deployed
2026-09-04 21:13:54 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:c590b315 · snapshot:pre-deploy-maya-hi-out-2026-09-04_211354 · deployed
2026-09-04 21:13:56 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b60bd535 · snapshot:pre-deploy-maya-hi-in-2026-09-04_211355 · deployed
2026-09-04 21:20:55 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:1f46a554 · snapshot:pre-deploy-trrain-kn-out-2026-09-04_212055 · deployed
2026-09-04 21:20:56 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:600a652e · snapshot:- · skip-in-sync
2026-09-04 21:22:58 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:9622b98c · snapshot:pre-deploy-maya-hi-signals-2026-09-04_212258 · deployed
2026-09-04 21:22:59 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:ecce7248 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_212259 · deployed
2026-09-04 21:23:00 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:57b89e4f · snapshot:pre-deploy-maya-hi-out-2026-09-04_212300 · deployed
2026-09-04 21:23:01 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:2c3557ed · snapshot:pre-deploy-maya-hi-in-2026-09-04_212301 · deployed
2026-09-04 21:32:13 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:ada9d7d1 · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_213212 · deployed
2026-09-04 21:32:15 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:4ba8658c · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_213214 · deployed
2026-09-04 21:32:17 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:f769925b · snapshot:pre-deploy-kkb-hi-out-2026-09-04_213216 · deployed
2026-09-04 21:32:19 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:0df201ec · snapshot:pre-deploy-kkb-kn-out-2026-09-04_213218 · deployed
2026-09-04 21:32:21 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:ad28b73e · snapshot:pre-deploy-maya-hi-signals-2026-09-04_213220 · deployed
2026-09-04 21:32:22 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:4f4d8276 · snapshot:pre-deploy-maya-hi-out-2026-09-04_213221 · deployed
2026-09-04 22:09:02 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:fe46ade6 · snapshot:pre-deploy-maya-hi-signals-2026-09-04_220901 · deployed
2026-09-04 22:09:03 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b59c8ce3 · snapshot:pre-deploy-maya-hi-out-2026-09-04_220902 · deployed
2026-09-04 22:10:30 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:d7b64757 · snapshot:pre-deploy-maya-hi-signals-2026-09-04_221029 · deployed
2026-09-04 22:10:31 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:f4f6ad85 · snapshot:pre-deploy-maya-hi-out-2026-09-04_221031 · deployed
2026-09-04 22:10:33 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:58fe69ca · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_221032 · deployed
2026-09-04 22:10:35 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:50577131 · snapshot:pre-deploy-maya-hi-in-2026-09-04_221034 · deployed
2026-09-04 22:12:54 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:76c35fb9 · snapshot:pre-deploy-kkb-hi-signals-2026-09-04_221253 · deployed
2026-09-04 22:12:56 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:935d18fc · snapshot:pre-deploy-kkb-kn-signals-2026-09-04_221255 · deployed
2026-09-04 22:12:56 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:55322679 · snapshot:pre-deploy-trrain-hi-out-2026-09-04_221256 · deployed
2026-09-04 22:12:57 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:f1753ecd · snapshot:pre-deploy-trrain-kn-out-2026-09-04_221257 · deployed
2026-09-04 22:24:51 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:cbbe386b · snapshot:pre-deploy-maya-hi-signals-2026-09-04_222450 · deployed
2026-09-04 22:24:53 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:71198238 · snapshot:pre-deploy-maya-hi-out-2026-09-04_222452 · deployed
2026-09-04 22:36:31 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:21683516 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-04_223630 · deployed
2026-09-04 22:36:32 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:e434d8b1 · snapshot:pre-deploy-maya-hi-in-2026-09-04_223632 · deployed
2026-09-04 22:52:18 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:07ceb417 · snapshot:pre-deploy-maya-hi-signals-2026-09-04_225217 · deployed
2026-09-04 22:52:19 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:99724735 · snapshot:pre-deploy-maya-hi-out-2026-09-04_225218 · deployed
2026-09-04 22:57:09 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:1ef3f5bb · snapshot:pre-deploy-maya-hi-signals-2026-09-04_225708 · deployed
2026-09-04 22:57:10 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:03e1d326 · snapshot:pre-deploy-maya-hi-out-2026-09-04_225710 · deployed
2026-09-04 23:03:12 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:3523e522 · snapshot:pre-deploy-dkb-hi-out-2026-09-04_230310 · deployed
2026-09-04 23:03:13 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:a13458fc · snapshot:- · skip-in-sync
2026-09-04 23:03:36 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:54ef2675 · snapshot:pre-deploy-dkb-kn-out-2026-09-04_230335 · deployed
2026-09-07 16:05:11 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:9a2dd8fa · snapshot:pre-deploy-dkb-hi-out-2026-09-07_160510 · deployed
2026-09-07 16:05:14 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:1a6f59d9 · snapshot:pre-deploy-dkb-kn-out-2026-09-07_160512 · deployed
2026-09-07 16:14:38 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:eea9dcd8 · snapshot:pre-deploy-kkb-hi-signals-2026-09-07_161437 · deployed
2026-09-07 16:14:40 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:61d84cfd · snapshot:pre-deploy-kkb-kn-signals-2026-09-07_161439 · deployed
2026-09-07 16:14:42 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:60eda94e · snapshot:pre-deploy-kkb-hi-out-2026-09-07_161441 · deployed
2026-09-07 16:14:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:a0c8ec78 · snapshot:pre-deploy-kkb-kn-out-2026-09-07_161445 · deployed
2026-09-07 16:14:47 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:aaac26d9 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-07_161446 · deployed
2026-09-07 16:14:49 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:f6a318cd · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-07_161448 · deployed
2026-09-07 16:14:52 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:519d1ae3 · snapshot:pre-deploy-kkb-hi-in-2026-09-07_161451 · deployed
2026-09-07 16:14:54 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:3dd7460e · snapshot:pre-deploy-kkb-kn-in-2026-09-07_161453 · deployed
2026-09-07 16:14:56 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:d11d2cf7 · snapshot:pre-deploy-maya-hi-signals-2026-09-07_161455 · deployed
2026-09-07 16:15:02 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:19b9c34e · snapshot:pre-deploy-maya-hi-in-signals-2026-09-07_161457 · deployed
2026-09-07 16:15:04 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:01e91e3f · snapshot:pre-deploy-maya-hi-out-2026-09-07_161503 · deployed
2026-09-07 16:15:06 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:63253373 · snapshot:pre-deploy-maya-hi-in-2026-09-07_161505 · deployed
2026-09-07 23:19:16 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:648a63db · snapshot:pre-deploy-kkb-hi-signals-2026-09-07_231915 · deployed
2026-09-07 23:19:17 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:bd31795d · snapshot:pre-deploy-kkb-kn-signals-2026-09-07_231917 · deployed
2026-09-07 23:19:19 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ab017380 · snapshot:pre-deploy-kkb-hi-out-2026-09-07_231918 · deployed
2026-09-07 23:19:20 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:07bf7015 · snapshot:pre-deploy-kkb-kn-out-2026-09-07_231920 · deployed
2026-09-07 23:19:22 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:be1d9c88 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-07_231921 · deployed
2026-09-07 23:19:23 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:3d1cd753 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-07_231923 · deployed
2026-09-07 23:19:25 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:0db877a4 · snapshot:pre-deploy-maya-hi-signals-2026-09-07_231924 · deployed
2026-09-07 23:19:26 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:918aefed · snapshot:pre-deploy-maya-hi-in-signals-2026-09-07_231926 · deployed
2026-09-07 23:34:21 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:0b759b03 · snapshot:pre-deploy-kkb-hi-signals-2026-09-07_233420 · deployed
2026-09-07 23:34:23 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:4c1a1a4f · snapshot:pre-deploy-kkb-kn-signals-2026-09-07_233422 · deployed
2026-09-07 23:34:25 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:d6bff656 · snapshot:pre-deploy-kkb-hi-out-2026-09-07_233424 · deployed
2026-09-07 23:34:26 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:57ef319b · snapshot:pre-deploy-kkb-kn-out-2026-09-07_233425 · deployed
2026-09-07 23:34:27 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:659f4d85 · snapshot:pre-deploy-maya-hi-signals-2026-09-07_233427 · deployed
2026-09-07 23:34:29 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e9b6e9f0 · snapshot:pre-deploy-maya-hi-out-2026-09-07_233428 · deployed
2026-09-08 12:16:24 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:e3096ea5 · snapshot:pre-deploy-kkb-hi-signals-2026-09-08_121623 · deployed
2026-09-08 12:16:26 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:50dc2ea4 · snapshot:pre-deploy-kkb-kn-signals-2026-09-08_121625 · deployed
2026-09-08 12:16:28 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:3ee6322e · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-08_121627 · deployed
2026-09-08 12:16:30 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:7fd201f2 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-08_121629 · deployed
2026-09-08 12:16:31 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7edbf4e1 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_121631 · deployed
2026-09-08 12:16:33 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:0451af95 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-08_121632 · deployed
2026-09-08 12:16:39 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:f99c2288 · snapshot:pre-deploy-kkb-hi-out-2026-09-08_121638 · deployed
2026-09-08 12:16:40 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:ddffe730 · snapshot:pre-deploy-kkb-kn-out-2026-09-08_121639 · deployed
2026-09-08 12:16:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:08a277a6 · snapshot:pre-deploy-kkb-hi-in-2026-09-08_121641 · deployed
2026-09-08 12:16:43 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:76d82b6d · snapshot:pre-deploy-kkb-kn-in-2026-09-08_121643 · deployed
2026-09-08 12:16:45 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:35f4f4a7 · snapshot:pre-deploy-maya-hi-out-2026-09-08_121644 · deployed
2026-09-08 12:16:47 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:8ce85a8c · snapshot:pre-deploy-maya-hi-in-2026-09-08_121646 · deployed
2026-09-08 12:16:48 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:7285595c · snapshot:pre-deploy-dkb-hi-out-2026-09-08_121648 · deployed
2026-09-08 12:16:50 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:73a46c8a · snapshot:pre-deploy-dkb-kn-out-2026-09-08_121649 · deployed
2026-09-08 12:16:51 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:7f2b1615 · snapshot:pre-deploy-dkb-hi-signals-2026-09-08_121650 · deployed
2026-09-08 12:16:52 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:a77238cb · snapshot:pre-deploy-dkb-kn-signals-2026-09-08_121652 · deployed
2026-09-08 19:35:08 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:5f580ed6 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_193456 · deployed
2026-09-08 19:35:16 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:680ccfb4 · snapshot:pre-deploy-maya-hi-out-2026-09-08_193511 · deployed
2026-09-08 19:44:02 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f6dd5c49 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_194356 · deployed
2026-09-08 19:51:37 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:be0fe757 · snapshot:pre-deploy-kkb-hi-signals-2026-09-08_195132 · deployed
2026-09-08 19:51:44 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:59067342 · snapshot:pre-deploy-kkb-kn-signals-2026-09-08_195142 · deployed
2026-09-08 19:51:48 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:48cea428 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-08_195146 · deployed
2026-09-08 19:51:53 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:02d020a7 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-08_195149 · deployed
2026-09-08 19:51:57 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:e0484f61 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_195155 · deployed
2026-09-08 19:52:07 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:19b67fdc · snapshot:pre-deploy-maya-hi-in-signals-2026-09-08_195202 · deployed
2026-09-08 19:52:20 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:446735d3 · snapshot:pre-deploy-kkb-hi-out-2026-09-08_195210 · deployed
2026-09-08 19:52:28 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:7f4a12b5 · snapshot:pre-deploy-kkb-kn-out-2026-09-08_195222 · deployed
2026-09-08 19:52:34 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:05a67c53 · snapshot:pre-deploy-kkb-hi-in-2026-09-08_195230 · deployed
2026-09-08 19:52:38 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:6784f6ad · snapshot:pre-deploy-kkb-kn-in-2026-09-08_195236 · deployed
2026-09-08 19:52:43 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:b9879274 · snapshot:pre-deploy-maya-hi-out-2026-09-08_195242 · deployed
2026-09-08 19:52:50 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:48dae7f3 · snapshot:pre-deploy-maya-hi-in-2026-09-08_195247 · deployed
2026-09-08 20:14:17 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:4b6b7c5a · snapshot:pre-deploy-dkb-hi-out-2026-09-08_201415 · deployed
2026-09-08 20:14:22 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:d592e631 · snapshot:pre-deploy-dkb-kn-out-2026-09-08_201418 · deployed
2026-09-08 20:14:32 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:bdcd86b5 · snapshot:pre-deploy-dkb-hi-signals-2026-09-08_201426 · deployed
2026-09-08 20:14:45 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:896949c1 · snapshot:pre-deploy-dkb-kn-signals-2026-09-08_201436 · deployed
2026-09-08 20:14:53 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:fea6c493 · snapshot:pre-deploy-trrain-hi-out-2026-09-08_201447 · deployed
2026-09-08 20:14:59 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:4bd9e75e · snapshot:pre-deploy-trrain-kn-out-2026-09-08_201455 · deployed
2026-09-08 20:15:33 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:fd24121d · snapshot:pre-deploy-kkb-hi-signals-2026-09-08_201518 · deployed
2026-09-08 20:17:03 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:51054c71 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-08_201655 · deployed
2026-09-08 20:17:09 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:c56852e8 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_201705 · deployed
2026-09-08 20:17:15 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:da040f42 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-08_201713 · deployed
2026-09-08 20:17:23 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:e5d9343a · snapshot:pre-deploy-kkb-hi-out-2026-09-08_201718 · deployed
2026-09-08 20:17:28 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:d17d98a7 · snapshot:pre-deploy-kkb-kn-out-2026-09-08_201726 · deployed
2026-09-08 20:17:32 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:b19e6e43 · snapshot:pre-deploy-kkb-hi-in-2026-09-08_201731 · deployed
2026-09-08 20:17:38 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:2dbc1e18 · snapshot:pre-deploy-kkb-kn-in-2026-09-08_201734 · deployed
2026-09-08 20:17:43 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:36354835 · snapshot:pre-deploy-maya-hi-out-2026-09-08_201740 · deployed
2026-09-08 20:17:49 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:f086e930 · snapshot:pre-deploy-maya-hi-in-2026-09-08_201746 · deployed
2026-09-08 20:17:53 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:64059997 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_201752 · deployed
2026-09-08 20:19:26 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f32fb5de · snapshot:pre-deploy-kkb-kn-signals-2026-09-08_201920 · deployed
2026-09-08 20:19:57 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f32fb5de · snapshot:- · skip-in-sync
2026-09-08 20:19:59 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:89200b51 · snapshot:- · skip-in-sync
2026-09-08 20:32:51 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:6e3c4859 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_203249 · deployed
2026-09-08 20:43:40 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:b0feaff2 · snapshot:pre-deploy-kkb-hi-signals-2026-09-08_204335 · deployed
2026-09-08 20:43:57 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:098ff977 · snapshot:pre-deploy-kkb-kn-signals-2026-09-08_204341 · deployed
2026-09-08 20:44:04 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:270c00c5 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-08_204401 · deployed
2026-09-08 20:44:14 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:f95e5c71 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-08_204406 · deployed
2026-09-08 20:44:20 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:01d08215 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_204417 · deployed
2026-09-08 20:44:26 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:328ad1c6 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-08_204422 · deployed
2026-09-08 20:44:30 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:2f45e011 · snapshot:pre-deploy-dkb-hi-out-2026-09-08_204429 · deployed
2026-09-08 20:44:35 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:a7cc484b · snapshot:pre-deploy-dkb-kn-out-2026-09-08_204434 · deployed
2026-09-08 20:44:40 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:8c23f33e · snapshot:pre-deploy-dkb-hi-signals-2026-09-08_204437 · deployed
2026-09-08 20:44:44 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:8abd7532 · snapshot:pre-deploy-dkb-kn-signals-2026-09-08_204441 · deployed
2026-09-08 21:03:32 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:64059997 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_210331 · deployed
2026-09-08 21:10:09 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:3425eb52 · snapshot:pre-deploy-kkb-hi-signals-2026-09-08_211006 · deployed
2026-09-08 21:10:17 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:2bdd20ee · snapshot:pre-deploy-kkb-kn-signals-2026-09-08_211012 · deployed
2026-09-08 21:10:23 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:e0e0aa5b · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-08_211019 · deployed
2026-09-08 21:10:27 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:8cc80ff6 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-08_211025 · deployed
2026-09-08 21:10:36 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:ba95ad46 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_211029 · deployed
2026-09-08 21:10:42 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:e7b98c6e · snapshot:pre-deploy-maya-hi-in-signals-2026-09-08_211038 · deployed
2026-09-08 21:10:50 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:24a2f3e5 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_211044 · deployed
2026-09-08 21:11:23 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f0fb13a9 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_211121 · deployed
2026-09-08 21:14:36 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:a080ce88 · snapshot:pre-deploy-kkb-hi-signals-2026-09-08_211435 · deployed
2026-09-08 21:14:41 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:ee938c68 · snapshot:pre-deploy-kkb-kn-signals-2026-09-08_211440 · deployed
2026-09-08 21:14:45 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:8c2830bc · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-08_211443 · deployed
2026-09-08 21:15:03 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:cf5925af · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-08_211446 · deployed
2026-09-08 21:15:07 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:a4377bfd · snapshot:pre-deploy-maya-hi-signals-2026-09-08_211504 · deployed
2026-09-08 21:15:13 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:185f12e2 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-08_211510 · deployed
2026-09-08 21:15:25 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:5281c1f7 · snapshot:pre-deploy-kkb-hi-in-2026-09-08_211514 · deployed
2026-09-08 21:15:29 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:790cb42f · snapshot:pre-deploy-kkb-kn-in-2026-09-08_211527 · deployed
2026-09-08 21:15:31 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:29790bb5 · snapshot:pre-deploy-maya-hi-out-2026-09-08_211530 · deployed
2026-09-08 21:15:46 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:c6256518 · snapshot:pre-deploy-maya-hi-in-2026-09-08_211534 · deployed
2026-09-08 21:15:49 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:2e03ba5b · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_211548 · deployed
2026-09-08 21:32:28 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:31aaa1f4 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_213223 · deployed
2026-09-08 21:32:32 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:67767644 · snapshot:pre-deploy-maya-hi-out-2026-09-08_213230 · deployed
2026-09-08 21:37:55 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:09369c33 · snapshot:pre-deploy-maya-hi-signals-2026-09-08_213753 · deployed
2026-09-08 21:38:01 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:235e1dd5 · snapshot:pre-deploy-maya-hi-out-2026-09-08_213759 · deployed
2026-09-08 21:39:20 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:1524c87b · snapshot:pre-deploy-dkb-hi-out-2026-09-08_213916 · deployed
2026-09-08 21:39:22 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:e2f77e3e · snapshot:pre-deploy-dkb-kn-out-2026-09-08_213921 · deployed
2026-09-08 21:39:24 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:4a759ba8 · snapshot:pre-deploy-dkb-hi-signals-2026-09-08_213923 · deployed
2026-09-08 21:39:28 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:35d07a66 · snapshot:pre-deploy-dkb-kn-signals-2026-09-08_213925 · deployed
2026-09-08 21:47:02 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:af195144 · snapshot:pre-deploy-dkb-hi-out-2026-09-08_214701 · deployed
2026-09-08 21:47:09 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:40711947 · snapshot:pre-deploy-dkb-kn-out-2026-09-08_214706 · deployed
2026-09-08 21:47:12 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:dd55e9f9 · snapshot:pre-deploy-dkb-hi-signals-2026-09-08_214710 · deployed
2026-09-08 21:47:29 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:3b2159d2 · snapshot:pre-deploy-dkb-kn-signals-2026-09-08_214728 · deployed
2026-09-08 21:50:57 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:42e91998 · snapshot:pre-deploy-kkb-hi-out-2026-09-08_215056 · deployed
2026-09-08 21:51:02 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:6bce0bbe · snapshot:pre-deploy-kkb-kn-out-2026-09-08_215059 · deployed
2026-09-08 21:51:13 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:b2aad6ff · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_215104 · deployed
2026-09-08 21:58:35 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:0d1a5753 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-08_215833 · deployed
2026-09-09 00:09:03 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:48a6108c · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_000901 · deployed
2026-09-09 00:24:51 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:495d3449 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_002448 · deployed
2026-09-09 00:24:55 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:5632c3c0 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_002453 · deployed
2026-09-09 00:25:00 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:495d3449 · snapshot:- · skip-in-sync
2026-09-09 00:25:04 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:5632c3c0 · snapshot:- · skip-in-sync
2026-09-09 00:35:35 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:53642951 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_003533 · deployed
2026-09-09 00:35:39 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:757727e0 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_003538 · deployed
2026-09-09 00:35:43 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:955174ac · snapshot:pre-deploy-kkb-hi-out-2026-09-09_003541 · deployed
2026-09-09 00:35:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:aa1ba031 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_003545 · deployed
2026-09-09 00:35:50 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:ba8a6977 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_003548 · deployed
2026-09-09 00:35:54 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:552c0965 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_003552 · deployed
2026-09-09 00:35:58 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:7d1b07ab · snapshot:pre-deploy-maya-hi-signals-2026-09-09_003556 · deployed
2026-09-09 00:36:03 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:5c083df2 · snapshot:pre-deploy-maya-hi-out-2026-09-09_003559 · deployed
2026-09-09 00:36:07 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:7422e444 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_003605 · deployed
2026-09-09 00:36:11 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:b07dd50d · snapshot:pre-deploy-maya-hi-in-2026-09-09_003609 · deployed
2026-09-09 00:36:14 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:ff4ad010 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_003613 · deployed
2026-09-09 00:36:39 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:9111c092 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_003637 · deployed
2026-09-09 00:36:45 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:503e965c · snapshot:pre-deploy-kkb-kn-in-2026-09-09_003641 · deployed
2026-09-09 00:51:36 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:90dad2c3 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_005133 · deployed
2026-09-09 00:51:42 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:bc03dec8 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_005138 · deployed
2026-09-09 00:51:47 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:2e1b38c6 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_005145 · deployed
2026-09-09 00:51:50 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:6d843571 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_005149 · deployed
2026-09-09 00:51:54 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:187f1aab · snapshot:pre-deploy-maya-hi-out-2026-09-09_005153 · deployed
2026-09-09 01:03:19 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:4636fe76 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_010316 · deployed
2026-09-09 01:03:24 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:9127357a · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_010322 · deployed
2026-09-09 01:03:29 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:ed11a85a · snapshot:pre-deploy-kkb-hi-out-2026-09-09_010327 · deployed
2026-09-09 01:03:33 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:551b2294 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_010331 · deployed
2026-09-09 01:03:37 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:8558a709 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_010335 · deployed
2026-09-09 01:03:40 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:52da81ba · snapshot:pre-deploy-kkb-kn-in-2026-09-09_010338 · deployed
2026-09-09 01:03:44 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:7f7cb8d1 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_010342 · deployed
2026-09-09 01:03:47 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:506fe89f · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_010345 · deployed
2026-09-09 01:03:52 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:4b8d362a · snapshot:pre-deploy-maya-hi-signals-2026-09-09_010349 · deployed
2026-09-09 01:03:55 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:f4ad972c · snapshot:pre-deploy-maya-hi-out-2026-09-09_010354 · deployed
2026-09-09 01:03:59 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:03cbb03a · snapshot:pre-deploy-maya-hi-in-2026-09-09_010357 · deployed
2026-09-09 01:04:03 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:845d5bf2 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_010401 · deployed
2026-09-09 01:04:04 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:fea6c493 · snapshot:- · skip-in-sync
2026-09-09 01:04:06 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:4bd9e75e · snapshot:- · skip-in-sync
2026-09-09 01:04:09 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:ff4ad010 · snapshot:- · skip-in-sync
2026-09-09 01:14:12 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:b3aae834 · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_011411 · deployed
2026-09-09 01:14:15 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:d1b1a5ff · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_011414 · deployed
2026-09-09 01:14:18 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:12d99165 · snapshot:pre-deploy-dkb-hi-out-2026-09-09_011417 · deployed
2026-09-09 01:14:21 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:61a43ea8 · snapshot:pre-deploy-dkb-kn-out-2026-09-09_011420 · deployed
2026-09-09 01:14:24 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:e4649926 · snapshot:pre-deploy-trrain-hi-out-2026-09-09_011423 · deployed
2026-09-09 01:14:26 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:7d781c4a · snapshot:pre-deploy-trrain-kn-out-2026-09-09_011425 · deployed
2026-09-09 01:14:28 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:83d039e8 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_011427 · deployed
2026-09-09 01:14:32 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:76c57724 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_011430 · deployed
2026-09-09 01:14:35 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:9de633ea · snapshot:pre-deploy-kkb-hi-out-2026-09-09_011433 · deployed
2026-09-09 01:14:38 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:ca1b542b · snapshot:pre-deploy-kkb-kn-out-2026-09-09_011436 · deployed
2026-09-09 01:14:40 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:ee7a2db6 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_011439 · deployed
2026-09-09 01:14:43 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:6e73f3c9 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_011442 · deployed
2026-09-09 01:14:46 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:9bcfb2d4 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_011445 · deployed
2026-09-09 01:14:49 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:4999ab9f · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_011448 · deployed
2026-09-09 01:14:52 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:2d557d77 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_011451 · deployed
2026-09-09 01:14:55 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:6c7e05dc · snapshot:pre-deploy-maya-hi-out-2026-09-09_011454 · deployed
2026-09-09 01:14:57 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:e6b722be · snapshot:pre-deploy-maya-hi-in-2026-09-09_011456 · deployed
2026-09-09 01:15:00 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:d0c2360c · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_011459 · deployed
2026-09-09 01:15:03 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:570b5707 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_011502 · deployed
2026-09-09 01:15:11 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:570b5707 · snapshot:- · skip-in-sync
2026-09-09 01:22:43 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:8ef286f0 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_012242 · deployed
2026-09-09 01:22:46 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:ccaad05c · snapshot:pre-deploy-dkb-kn-out-2026-09-09_012245 · deployed
2026-09-09 01:23:39 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:0df04aca · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_012338 · deployed
2026-09-09 01:23:42 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:26655e57 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_012341 · deployed
2026-09-09 01:23:44 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:a685013b · snapshot:pre-deploy-dkb-hi-out-2026-09-09_012343 · deployed
2026-09-09 01:23:47 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:90c19460 · snapshot:pre-deploy-dkb-kn-out-2026-09-09_012346 · deployed
2026-09-09 01:26:16 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:0a540fe8 · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_012615 · deployed
2026-09-09 01:26:20 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:6a430bc9 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_012618 · deployed
2026-09-09 01:26:22 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:3fb7608a · snapshot:pre-deploy-dkb-hi-out-2026-09-09_012621 · deployed
2026-09-09 01:26:26 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:4189fcb2 · snapshot:pre-deploy-dkb-kn-out-2026-09-09_012624 · deployed
2026-09-09 02:00:09 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:e2ef0bc7 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_020008 · deployed
2026-09-09 02:00:11 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:a63d84cf · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_020010 · deployed
2026-09-09 02:00:13 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:98609420 · snapshot:pre-deploy-kkb-hi-out-2026-09-09_020012 · deployed
2026-09-09 02:00:15 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:2ed28577 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_020014 · deployed
2026-09-09 02:00:17 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:237028a8 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_020016 · deployed
2026-09-09 02:00:19 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:94202284 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_020018 · deployed
2026-09-09 02:00:20 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:989196d3 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_020020 · deployed
2026-09-09 02:00:22 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:8e3c8d1f · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_020021 · deployed
2026-09-09 02:00:24 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:76e38b14 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_020023 · deployed
2026-09-09 02:00:26 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:f0584ebf · snapshot:pre-deploy-maya-hi-out-2026-09-09_020025 · deployed
2026-09-09 02:00:28 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:a601fe27 · snapshot:pre-deploy-maya-hi-in-2026-09-09_020027 · deployed
2026-09-09 02:00:30 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:acd75d45 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_020029 · deployed
2026-09-09 02:00:32 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:edb94d2d · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_020031 · deployed
2026-09-09 02:05:40 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:8c42858d · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_020539 · deployed
2026-09-09 02:05:42 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:ab0fe5fc · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_020541 · deployed
2026-09-09 02:05:44 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:38d4b08f · snapshot:pre-deploy-kkb-hi-out-2026-09-09_020543 · deployed
2026-09-09 02:05:46 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:614b4612 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_020545 · deployed
2026-09-09 02:05:48 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:c9a94405 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_020547 · deployed
2026-09-09 02:05:50 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:76343d82 · snapshot:pre-deploy-maya-hi-out-2026-09-09_020549 · deployed
2026-09-09 02:05:52 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:d74d6908 · snapshot:pre-deploy-maya-hi-in-2026-09-09_020551 · deployed
2026-09-09 02:05:54 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:5ebb8093 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_020553 · deployed
2026-09-09 02:05:56 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:5d2b07ef · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_020555 · deployed
2026-09-09 02:06:17 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:29014fdb · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_020616 · deployed
2026-09-09 02:20:08 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:22947efc · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_022007 · deployed
2026-09-09 02:20:10 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:76b62761 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_022009 · deployed
2026-09-09 02:58:38 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:83d68308 · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_025837 · deployed
2026-09-09 02:58:39 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:a00b6099 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_025839 · deployed
2026-09-09 02:58:41 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:1eb5caed · snapshot:pre-deploy-dkb-hi-out-2026-09-09_025840 · deployed
2026-09-09 02:58:42 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:c285713b · snapshot:pre-deploy-dkb-kn-out-2026-09-09_025842 · deployed
2026-09-09 03:00:06 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:1010e40c · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_030005 · deployed
2026-09-09 03:00:07 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:2d0d0606 · snapshot:pre-deploy-dkb-hi-out-2026-09-09_030007 · deployed
2026-09-09 03:00:09 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:be781117 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_030008 · deployed
2026-09-09 03:00:11 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:ea927146 · snapshot:pre-deploy-dkb-kn-out-2026-09-09_030010 · deployed
2026-09-09 03:00:37 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:1010e40c · snapshot:- · skip-in-sync
2026-09-09 03:00:38 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:2d0d0606 · snapshot:- · skip-in-sync
2026-09-09 03:00:39 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:5f485c82 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_030039 · deployed
2026-09-09 03:00:41 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:6e82a931 · snapshot:pre-deploy-dkb-kn-out-2026-09-09_030040 · deployed
2026-09-09 03:00:55 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:db72febe · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_030055 · deployed
2026-09-09 03:00:57 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:b6d9d57e · snapshot:pre-deploy-dkb-hi-out-2026-09-09_030056 · deployed
2026-09-09 03:07:09 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:db72febe · snapshot:- · skip-in-sync
2026-09-09 03:07:10 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:b6d9d57e · snapshot:- · skip-in-sync
2026-09-09 03:07:12 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:858d3dd7 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_030711 · deployed
2026-09-09 03:07:13 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:f86c589f · snapshot:pre-deploy-dkb-kn-out-2026-09-09_030712 · deployed
2026-09-09 03:19:18 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:a77adce7 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_031916 · deployed
2026-09-09 03:19:20 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f332d041 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_031919 · deployed
2026-09-09 03:19:21 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:e5b08edb · snapshot:pre-deploy-kkb-hi-out-2026-09-09_031921 · deployed
2026-09-09 03:19:23 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:7a1996b0 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_031922 · deployed
2026-09-09 03:19:25 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:0c1d2a30 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_031924 · deployed
2026-09-09 03:19:27 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:9b0acb63 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_031926 · deployed
2026-09-09 03:19:29 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:f58a558b · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_031928 · deployed
2026-09-09 03:19:31 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:7643f5b9 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_031930 · deployed
2026-09-09 03:19:33 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:199a888c · snapshot:pre-deploy-maya-hi-signals-2026-09-09_031932 · deployed
2026-09-09 03:19:35 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:416f726c · snapshot:pre-deploy-maya-hi-out-2026-09-09_031934 · deployed
2026-09-09 03:19:37 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:3bcdf66d · snapshot:pre-deploy-maya-hi-in-2026-09-09_031936 · deployed
2026-09-09 03:19:39 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:f4f42322 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_031938 · deployed
2026-09-09 03:19:41 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:7882a03d · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_031940 · deployed
2026-09-09 03:25:08 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:76e3f77c · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_032507 · deployed
2026-09-09 03:25:10 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:fc053bd2 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_032509 · deployed
2026-09-09 03:35:29 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:aae506ec · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_033529 · deployed
2026-09-09 03:35:31 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:681c072c · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_033530 · deployed
2026-09-09 03:35:33 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:22245d29 · snapshot:pre-deploy-dkb-hi-out-2026-09-09_033532 · deployed
2026-09-09 03:35:34 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:bc25eac9 · snapshot:pre-deploy-dkb-kn-out-2026-09-09_033533 · deployed
2026-09-09 03:35:36 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:69f187fb · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_033535 · deployed
2026-09-09 03:35:38 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:5fe4b270 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_033537 · deployed
2026-09-09 03:35:40 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:53650eae · snapshot:pre-deploy-kkb-hi-out-2026-09-09_033539 · deployed
2026-09-09 03:35:42 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:eaaa3bc5 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_033541 · deployed
2026-09-09 03:35:44 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:245f9fa9 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_033543 · deployed
2026-09-09 03:35:46 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:af128aea · snapshot:pre-deploy-kkb-kn-in-2026-09-09_033545 · deployed
2026-09-09 03:35:48 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:19da5581 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_033547 · deployed
2026-09-09 03:35:50 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:2821d115 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_033548 · deployed
2026-09-09 03:35:51 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:92923139 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_033550 · deployed
2026-09-09 03:35:53 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:1710ce3f · snapshot:pre-deploy-maya-hi-out-2026-09-09_033552 · deployed
2026-09-09 03:35:55 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:1b847508 · snapshot:pre-deploy-maya-hi-in-2026-09-09_033554 · deployed
2026-09-09 03:35:57 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:54924d15 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_033556 · deployed
2026-09-09 03:35:59 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:3393691f · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_033558 · deployed
2026-09-09 03:46:55 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:c78cdb0b · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_034654 · deployed
2026-09-09 03:46:57 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:6f35b508 · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_034656 · deployed
2026-09-09 03:46:59 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:aa3f554e · snapshot:pre-deploy-dkb-hi-out-2026-09-09_034658 · deployed
2026-09-09 03:47:00 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:43a6835e · snapshot:pre-deploy-dkb-kn-out-2026-09-09_034700 · deployed
2026-09-09 04:24:09 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:cddd9245 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_042408 · deployed
2026-09-09 04:24:11 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:92eddd21 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_042410 · deployed
2026-09-09 04:24:13 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:d9b6d612 · snapshot:pre-deploy-kkb-hi-out-2026-09-09_042412 · deployed
2026-09-09 04:24:15 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:d0a8895b · snapshot:pre-deploy-kkb-kn-out-2026-09-09_042414 · deployed
2026-09-09 04:24:17 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:13c665c8 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_042416 · deployed
2026-09-09 04:24:19 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:3b687728 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_042418 · deployed
2026-09-09 04:24:21 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:92310a57 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_042420 · deployed
2026-09-09 04:24:23 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:e8ccf222 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_042422 · deployed
2026-09-09 04:24:25 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:3c301cbc · snapshot:pre-deploy-maya-hi-signals-2026-09-09_042424 · deployed
2026-09-09 04:24:27 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:92bfc848 · snapshot:pre-deploy-maya-hi-out-2026-09-09_042426 · deployed
2026-09-09 04:24:29 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:09d53632 · snapshot:pre-deploy-maya-hi-in-2026-09-09_042428 · deployed
2026-09-09 04:24:31 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:70dfc8b6 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_042430 · deployed
2026-09-09 04:24:33 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:9a86f326 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_042432 · deployed
2026-09-09 04:29:26 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:d34bcfb7 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_042925 · deployed
2026-09-09 04:29:28 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:83cef9db · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_042927 · deployed
2026-09-09 04:29:30 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:07e20e69 · snapshot:pre-deploy-kkb-hi-out-2026-09-09_042929 · deployed
2026-09-09 04:29:32 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:0b22866f · snapshot:pre-deploy-kkb-kn-out-2026-09-09_042931 · deployed
2026-09-09 04:29:34 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:3ba5ff6e · snapshot:pre-deploy-kkb-hi-in-2026-09-09_042933 · deployed
2026-09-09 04:29:36 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:d4ce1b02 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_042935 · deployed
2026-09-09 04:29:38 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:ea768aa5 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_042937 · deployed
2026-09-09 04:29:40 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:dfad62dd · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_042939 · deployed
2026-09-09 04:29:42 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:a335e324 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_042941 · deployed
2026-09-09 04:29:44 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:21da1e87 · snapshot:pre-deploy-maya-hi-out-2026-09-09_042943 · deployed
2026-09-09 04:29:46 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:7223e875 · snapshot:pre-deploy-maya-hi-in-2026-09-09_042945 · deployed
2026-09-09 04:29:48 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:3afc0946 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_042947 · deployed
2026-09-09 04:29:50 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:1711f2ff · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_042949 · deployed
2026-09-09 05:12:27 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:13747fb0 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_051226 · deployed
2026-09-09 05:12:29 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:c2f89594 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_051228 · deployed
2026-09-09 05:12:31 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:d5811248 · snapshot:pre-deploy-kkb-hi-out-2026-09-09_051230 · deployed
2026-09-09 05:12:33 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:529c3552 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_051232 · deployed
2026-09-09 05:12:34 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:3ba5ff6e · snapshot:- · skip-in-sync
2026-09-09 05:12:35 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:d4ce1b02 · snapshot:- · skip-in-sync
2026-09-09 05:12:36 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:ea768aa5 · snapshot:- · skip-in-sync
2026-09-09 05:12:37 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:dfad62dd · snapshot:- · skip-in-sync
2026-09-09 05:12:38 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:a335e324 · snapshot:- · skip-in-sync
2026-09-09 05:12:39 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:21da1e87 · snapshot:- · skip-in-sync
2026-09-09 05:12:40 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:7223e875 · snapshot:- · skip-in-sync
2026-09-09 05:12:41 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:3afc0946 · snapshot:- · skip-in-sync
2026-09-09 05:12:42 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:1711f2ff · snapshot:- · skip-in-sync
2026-09-09 05:13:03 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:3ba5ff6e · snapshot:- · skip-in-sync
2026-09-09 05:13:04 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:ea768aa5 · snapshot:- · skip-in-sync
2026-09-09 05:13:06 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:2b78ce80 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_051305 · deployed
2026-09-09 05:13:09 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:81320461 · snapshot:pre-deploy-maya-hi-out-2026-09-09_051307 · deployed
2026-09-09 05:13:10 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:7223e875 · snapshot:- · skip-in-sync
2026-09-09 05:13:11 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:3afc0946 · snapshot:- · skip-in-sync
2026-09-09 05:13:12 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:1711f2ff · snapshot:- · skip-in-sync
2026-09-09 05:13:36 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:ebe81ab4 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_051335 · deployed
2026-09-09 05:35:26 · prod · maya-out-memory · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Memory.md · sha256:92bd4484 · snapshot:pre-deploy-maya-out-memory-2026-09-09_053526 · deployed
2026-09-09 05:35:28 · prod · maya-in-memory · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Memory.md · sha256:92bd4484 · snapshot:pre-deploy-maya-in-memory-2026-09-09_053527 · deployed
2026-09-09 05:52:07 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:c78cdb0b · snapshot:- · skip-in-sync
2026-09-09 05:52:08 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:6f35b508 · snapshot:- · skip-in-sync
2026-09-09 05:52:09 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:aa3f554e · snapshot:- · skip-in-sync
2026-09-09 05:52:09 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:43a6835e · snapshot:- · skip-in-sync
2026-09-09 05:52:40 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:8748153e · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_055239 · deployed
2026-09-09 05:52:41 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:1710676a · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_055240 · deployed
2026-09-09 05:52:43 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:34f28b81 · snapshot:pre-deploy-dkb-hi-out-2026-09-09_055242 · deployed
2026-09-09 05:52:45 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:e6b9f9ef · snapshot:pre-deploy-dkb-kn-out-2026-09-09_055244 · deployed
2026-09-09 06:04:49 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:63ac79a4 · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_060448 · deployed
2026-09-09 06:04:50 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:1710676a · snapshot:- · skip-in-sync
2026-09-09 06:04:51 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:244a9e76 · snapshot:pre-deploy-dkb-hi-out-2026-09-09_060451 · deployed
2026-09-09 06:04:52 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:e6b9f9ef · snapshot:- · skip-in-sync
2026-09-09 06:05:14 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:4fc38605 · snapshot:pre-deploy-dkb-hi-signals-2026-09-09_060513 · deployed
2026-09-09 06:05:16 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:20fb50cb · snapshot:pre-deploy-dkb-kn-signals-2026-09-09_060515 · deployed
2026-09-09 06:05:17 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:36387fcd · snapshot:pre-deploy-dkb-hi-out-2026-09-09_060516 · deployed
2026-09-09 06:05:19 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:519a5057 · snapshot:pre-deploy-dkb-kn-out-2026-09-09_060518 · deployed
2026-09-09 06:26:30 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:4d04228a · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_062629 · deployed
2026-09-09 06:26:32 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:23a32137 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_062631 · deployed
2026-09-09 06:26:34 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:a7642ea0 · snapshot:pre-deploy-kkb-hi-out-2026-09-09_062634 · deployed
2026-09-09 06:26:36 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:fc8ac8c4 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_062635 · deployed
2026-09-09 06:26:38 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:890b9f02 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_062637 · deployed
2026-09-09 06:26:40 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:5a56cfa0 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_062639 · deployed
2026-09-09 06:26:42 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:15cbefdc · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_062641 · deployed
2026-09-09 06:26:44 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:9e0e5f8a · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_062643 · deployed
2026-09-09 06:26:47 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:4c1137d3 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_062645 · deployed
2026-09-09 06:26:49 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:7c172f88 · snapshot:pre-deploy-maya-hi-out-2026-09-09_062648 · deployed
2026-09-09 06:26:50 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:09851c5a · snapshot:pre-deploy-maya-hi-in-2026-09-09_062649 · deployed
2026-09-09 06:26:52 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:70da40c4 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_062651 · deployed
2026-09-09 06:26:53 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:ebe81ab4 · snapshot:- · skip-in-sync
2026-09-09 06:32:52 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:1f6a17af · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_063251 · deployed
2026-09-09 06:32:54 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f2e17983 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_063253 · deployed
2026-09-09 06:32:57 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:c90d6bcf · snapshot:pre-deploy-kkb-hi-out-2026-09-09_063256 · deployed
2026-09-09 06:32:59 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:1d552795 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_063258 · deployed
2026-09-09 06:33:01 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:e6a61e7b · snapshot:pre-deploy-kkb-hi-in-2026-09-09_063300 · deployed
2026-09-09 06:33:03 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:5dc6bc7a · snapshot:pre-deploy-kkb-kn-in-2026-09-09_063302 · deployed
2026-09-09 06:33:05 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:76b2beaa · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_063304 · deployed
2026-09-09 06:33:07 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:f3c45cbe · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_063306 · deployed
2026-09-09 06:33:09 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:f539815b · snapshot:pre-deploy-maya-hi-signals-2026-09-09_063308 · deployed
2026-09-09 06:33:11 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:9e96e60c · snapshot:pre-deploy-maya-hi-out-2026-09-09_063310 · deployed
2026-09-09 06:33:13 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:08ead80f · snapshot:pre-deploy-maya-hi-in-2026-09-09_063312 · deployed
2026-09-09 06:33:15 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:e1e4826d · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_063314 · deployed
2026-09-09 07:06:48 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:522ff868 · snapshot:pre-deploy-kkb-hi-signals-2026-09-09_070647 · deployed
2026-09-09 07:06:50 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:e3361d26 · snapshot:pre-deploy-kkb-kn-signals-2026-09-09_070649 · deployed
2026-09-09 07:06:52 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:d16172cd · snapshot:pre-deploy-kkb-hi-out-2026-09-09_070651 · deployed
2026-09-09 07:06:54 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:812a72f9 · snapshot:pre-deploy-kkb-kn-out-2026-09-09_070653 · deployed
2026-09-09 07:06:56 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:c3deb0c0 · snapshot:pre-deploy-kkb-hi-in-2026-09-09_070655 · deployed
2026-09-09 07:06:58 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:307fdf28 · snapshot:pre-deploy-kkb-kn-in-2026-09-09_070657 · deployed
2026-09-09 07:07:00 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:53c6eb47 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-09_070659 · deployed
2026-09-09 07:07:02 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:7af8c811 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-09_070701 · deployed
2026-09-09 07:07:04 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:aba54237 · snapshot:pre-deploy-maya-hi-signals-2026-09-09_070703 · deployed
2026-09-09 07:07:06 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:237a9ac2 · snapshot:pre-deploy-maya-hi-out-2026-09-09_070705 · deployed
2026-09-09 07:07:08 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:12eb7665 · snapshot:pre-deploy-maya-hi-in-2026-09-09_070707 · deployed
2026-09-09 07:07:10 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:79cb36a1 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-09_070709 · deployed
2026-09-09 07:07:12 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:9b0d8ad1 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_070711 · deployed
2026-09-09 19:16:12 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:bad0a146 · snapshot:- · dry-run
2026-09-09 19:16:16 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:bad0a146 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_191616 · deployed
2026-09-09 19:31:30 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:27c115fd · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_193129 · deployed
2026-09-09 19:36:11 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:6708f74c · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_193610 · deployed
2026-09-09 19:45:47 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:20eb630d · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_194546 · deployed
2026-09-09 20:17:21 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:06fa1e0e · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-09_201720 · deployed
2026-09-10 19:58:55 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:be5a7f29 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_195854 · deployed
2026-09-10 20:08:50 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:ceeec9f7 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_200849 · deployed
2026-09-10 20:16:35 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:32196e94 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_201635 · deployed
2026-09-10 20:27:36 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:6afc73de · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_202735 · deployed
2026-09-10 20:46:25 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:b9a98292 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_204624 · deployed
2026-09-10 20:46:26 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:a757bd54 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-10_204625 · deployed
2026-09-10 20:59:03 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f9d9d884 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_205902 · deployed
2026-09-10 20:59:04 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:bab544ac · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-10_205903 · deployed
2026-09-10 21:08:52 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:0fee7280 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_210851 · deployed
2026-09-10 21:08:53 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:237c1fd6 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-10_210853 · deployed
2026-09-10 21:55:23 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f07a24a3 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_215523 · deployed
2026-09-10 21:55:25 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:b604f8c4 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-10_215524 · deployed
2026-09-10 22:35:53 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:52e18298 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_223552 · deployed
2026-09-10 22:35:55 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:8a577fad · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-10_223554 · deployed
2026-09-10 23:05:23 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:33a39dd6 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-10_230523 · deployed
2026-09-10 23:05:25 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:5b5a8a75 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-10_230524 · deployed
2026-09-22 20:57:28 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:ea24ccdc · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-22_205727 · deployed
2026-09-22 20:57:29 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:142f4652 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-22_205728 · deployed
2026-09-23 01:10:15 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:0669c724 · snapshot:pre-deploy-kkb-hi-signals-2026-09-23_011013 · deployed
2026-09-23 01:15:21 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:35aec582 · snapshot:pre-deploy-kkb-hi-signals-2026-09-23_011521 · deployed
2026-09-23 01:20:41 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:1567a054 · snapshot:pre-deploy-kkb-kn-signals-2026-09-23_012040 · deployed
2026-09-23 01:25:34 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:a29dada0 · snapshot:pre-deploy-kkb-kn-signals-2026-09-23_012531 · deployed
2026-09-23 01:30:55 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:84ec1516 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-23_013054 · deployed
2026-09-23 01:30:56 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:d71ce443 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-23_013055 · deployed
2026-09-23 01:30:58 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:f74cf717 · snapshot:pre-deploy-maya-hi-signals-2026-09-23_013057 · deployed
2026-09-23 01:30:59 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:58f46184 · snapshot:pre-deploy-maya-hi-in-signals-2026-09-23_013058 · deployed
2026-09-23 01:33:35 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:bb27db45 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_013335 · deployed
2026-09-23 01:33:36 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:5c5d8ace · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_013336 · deployed
2026-09-23 01:41:51 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:7d5fa695 · snapshot:pre-deploy-kkb-hi-signals-2026-09-23_014150 · deployed
2026-09-23 01:41:53 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:4f8c3d7b · snapshot:pre-deploy-kkb-kn-signals-2026-09-23_014152 · deployed
2026-09-23 01:41:56 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:d14a26a0 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-23_014155 · deployed
2026-09-23 01:41:57 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:684c37d8 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-23_014156 · deployed
2026-09-23 01:41:58 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:0d287fdd · snapshot:pre-deploy-maya-hi-signals-2026-09-23_014157 · deployed
2026-09-23 01:41:59 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:3bf5408d · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_014158 · deployed
2026-09-23 01:42:00 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:8c286b13 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_014159 · deployed
2026-09-23 01:46:02 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:c6bfe8eb · snapshot:pre-deploy-maya-hi-in-signals-2026-09-23_014601 · deployed
2026-09-23 01:52:10 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:70ff6b4a · snapshot:pre-deploy-maya-hi-in-signals-2026-09-23_015209 · deployed
2026-09-23 01:52:12 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:d796e886 · snapshot:pre-deploy-kkb-hi-in-signals-2026-09-23_015211 · deployed
2026-09-23 01:52:13 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:56276d76 · snapshot:pre-deploy-kkb-kn-in-signals-2026-09-23_015212 · deployed
2026-09-23 02:25:11 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:3ed559b8 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_022511 · deployed
2026-09-23 02:32:01 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f911bce5 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_023201 · deployed
2026-09-23 02:39:01 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:06a2a776 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_023901 · deployed
2026-09-23 02:39:26 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:d331cdb6 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_023925 · deployed
2026-09-23 02:48:32 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:8c5c7b59 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_024831 · deployed
2026-09-23 03:02:00 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f96ecfa5 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_030200 · deployed
2026-09-23 03:16:41 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:4f0afe7b · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_031640 · deployed
2026-09-23 03:17:32 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:4ccb602b · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_031731 · deployed
2026-09-23 03:21:48 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:05785093 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_032147 · deployed
2026-09-23 03:28:43 · prod · kkb-hi-signals-slim(output_instructions) · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Output.md · sha256:453bf5da · manual PATCH (adds field 26 call_direction; live adopted into a new slim-only file) · deployed
2026-09-23 10:37:34 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:1287d08b · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_103733 · deployed
2026-09-23 10:37:35 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:ea72e182 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_103735 · deployed
2026-09-23 11:25:46 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:20abc3f7 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_112546 · deployed
2026-09-23 11:25:47 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:09865a67 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_112547 · deployed
2026-09-23 13:29:43 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:996caaa9 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_132942 · deployed
2026-09-23 13:34:11 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:996caaa9 · snapshot:- · skip-in-sync
2026-09-23 13:34:37 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:20abc3f7 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_133436 · deployed
2026-09-23 13:37:15 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:62a5ed6d · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_133714 · deployed
2026-09-23 13:45:28 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:97a751e9 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_134528 · deployed
2026-09-23 13:54:07 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:00a9563f · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_135406 · deployed
2026-09-23 14:07:01 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f90e197b · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_140701 · deployed
2026-09-23 14:18:47 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:8ccda3c2 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_141846 · deployed
2026-09-23 15:18:38 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:93160595 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_151837 · deployed
2026-09-23 15:31:30 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:a113032c · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_153129 · deployed
2026-09-23 19:24:05 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:da5ebe99 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_192405 · deployed
2026-09-23 19:24:06 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:78f9a9db · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_192406 · deployed
2026-09-23 19:47:13 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:b9b4d92a · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_194712 · deployed
2026-09-23 19:47:14 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:7c925922 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_194714 · deployed
2026-09-23 20:01:57 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:35109c01 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_200156 · deployed
2026-09-23 20:01:57 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:c5081b19 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_200157 · deployed
2026-09-23 20:20:21 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:e53bf80a · snapshot:pre-deploy-kkb-hi-signals-slim-2026-09-23_202021 · deployed
2026-09-23 20:20:22 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:3613a20a · snapshot:pre-deploy-kkb-kn-signals-slim-2026-09-23_202022 · deployed
2026-10-05 13:02:59 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:cea78826 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-05_130259 · deployed
2026-10-05 19:39:02 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:bc004293 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-05_193901 · deployed
2026-10-12 08:18:20 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:c7fca31f · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-12_081819 · deployed
2026-10-12 08:18:20 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:97013109 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-12_081820 · deployed
2026-10-12 08:21:12 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:e7644c54 · snapshot:pre-deploy-maya-hi-out-2026-10-12_082112 · deployed
2026-10-12 08:21:13 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:ced970d7 · snapshot:pre-deploy-maya-hi-in-2026-10-12_082113 · deployed
2026-10-12 08:21:14 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:4f439b3a · snapshot:pre-deploy-maya-hi-signals-2026-10-12_082113 · deployed
2026-10-12 08:21:14 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:306b919f · snapshot:pre-deploy-maya-hi-in-signals-2026-10-12_082114 · deployed
2026-10-12 08:30:35 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:2268b866 · snapshot:pre-deploy-trrain-hi-out-2026-10-12_083035 · deployed
2026-10-12 08:30:35 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:6d748d23 · snapshot:pre-deploy-trrain-kn-out-2026-10-12_083035 · deployed
2026-10-12 08:30:36 · prod · trrain-hi-output · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Output.md · sha256:6b96ce8e · snapshot:pre-deploy-trrain-hi-output-2026-10-12_083036 · deployed
2026-10-12 08:30:36 · prod · trrain-kn-output · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Output.md · sha256:6b96ce8e · snapshot:pre-deploy-trrain-kn-output-2026-10-12_083036 · deployed
2026-10-12 08:43:44 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:693131b1 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-12_084344 · deployed
2026-10-12 08:43:45 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:4983ba81 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-12_084345 · deployed
2026-10-12 09:27:33 · prod · trrain-hi-output · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Output.md · sha256:3053e113 · snapshot:pre-deploy-trrain-hi-output-2026-10-12_092733 · deployed
2026-10-12 09:27:34 · prod · trrain-kn-output · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Output.md · sha256:3053e113 · snapshot:pre-deploy-trrain-kn-output-2026-10-12_092733 · deployed
2026-10-12 09:47:47 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:9068495f · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-12_094747 · deployed
2026-10-12 09:47:48 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:49645768 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-12_094747 · deployed
2026-10-13 12:42:06 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:e69cf86a · snapshot:pre-deploy-dkb-hi-signals-2026-10-13_124205 · deployed
2026-10-13 12:42:10 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:bb4bc2eb · snapshot:pre-deploy-dkb-kn-signals-2026-10-13_124208 · deployed
2026-10-13 12:42:14 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:2e4e9aa8 · snapshot:pre-deploy-maya-hi-signals-2026-10-13_124213 · deployed
2026-10-13 12:42:17 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:e25b318b · snapshot:pre-deploy-maya-hi-in-signals-2026-10-13_124216 · deployed
2026-10-13 12:42:22 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:f9fc75cf · snapshot:pre-deploy-kkb-hi-signals-2026-10-13_124219 · deployed
2026-10-13 12:42:25 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:7b230a7d · snapshot:pre-deploy-kkb-kn-signals-2026-10-13_124223 · deployed
2026-10-13 12:42:28 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:ce633599 · snapshot:pre-deploy-kkb-hi-in-signals-2026-10-13_124226 · deployed
2026-10-13 12:42:34 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:05113704 · snapshot:pre-deploy-kkb-kn-in-signals-2026-10-13_124233 · deployed
2026-10-13 12:46:03 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:b369ca42 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-13_124602 · deployed
2026-10-13 12:46:06 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:90803ce3 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-13_124605 · deployed
2026-10-13 07:16:18 · prod · kkb-hi-signals-slim+kkb-kn-signals-slim(output_instructions) · KKB-Slim/KKB Slim Output.md · manual PATCH (adds 12a callback_requested) · deployed
2026-10-13 07:31:54 · prod · kkb-hi-signals-slim+kkb-kn-signals-slim(output_instructions) · KKB-Slim/KKB Slim Output.md · manual PATCH (12a callback_requested is text, never a timestamp) · deployed
2026-10-13 07:45:11 · prod · kkb-hi-signals-slim+kkb-kn-signals-slim(output_instructions) · KKB-Slim/KKB Slim Output.md · manual PATCH (12a renamed call_later_request) · deployed
2026-10-13 13:20:29 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f384bf08 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-13_132028 · deployed
2026-10-13 13:20:33 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:1604b783 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-13_132031 · deployed
2026-10-13 13:20:35 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:47870812 · snapshot:pre-deploy-maya-hi-signals-2026-10-13_132034 · deployed
2026-10-13 13:20:38 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:6cc2b89d · snapshot:pre-deploy-maya-hi-in-signals-2026-10-13_132037 · deployed
2026-10-13 13:36:15 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:4bcfce17 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-13_133614 · deployed
2026-10-13 13:36:18 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:d128b36f · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-13_133617 · deployed
2026-10-13 13:36:52 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:adaf1c3d · snapshot:pre-deploy-maya-hi-signals-2026-10-13_133650 · deployed
2026-10-13 13:39:52 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:c1ad99b6 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-13_133951 · deployed
2026-10-13 13:39:55 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:9018ac9b · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-13_133954 · deployed
2026-10-13 13:44:48 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:9e1738c7 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-13_134447 · deployed
2026-10-13 13:44:51 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:96a78a98 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-13_134450 · deployed
2026-10-13 13:44:55 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:3b9e6868 · snapshot:pre-deploy-maya-hi-signals-2026-10-13_134453 · deployed
2026-10-13 13:44:58 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:151463b7 · snapshot:pre-deploy-maya-hi-in-signals-2026-10-13_134456 · deployed
2026-10-13 13:53:39 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:6f393cec · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-13_135338 · deployed
2026-10-13 13:53:42 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:ae6a5592 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-13_135341 · deployed
2026-10-13 13:59:13 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:fbaf615b · snapshot:pre-deploy-maya-hi-signals-2026-10-13_135912 · deployed
2026-10-13 13:59:19 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:3777cdfb · snapshot:pre-deploy-maya-hi-in-signals-2026-10-13_135918 · deployed
2026-10-19 14:27:09 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:4d6f04d3 · snapshot:pre-deploy-dkb-hi-signals-2026-10-19_142709 · deployed
2026-10-19 14:27:10 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:287e8b3a · snapshot:pre-deploy-dkb-kn-signals-2026-10-19_142710 · deployed
2026-10-19 14:36:22 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:f22db1ba · snapshot:pre-deploy-dkb-hi-signals-2026-10-19_143621 · deployed
2026-10-19 14:36:22 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:d0b8eaa8 · snapshot:pre-deploy-dkb-kn-signals-2026-10-19_143622 · deployed
2026-10-19 14:36:24 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f1f80352 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-19_143623 · deployed
2026-10-19 14:36:25 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:de2cbaa8 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-19_143624 · deployed
2026-10-19 14:42:28 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:579a75c2 · snapshot:pre-deploy-dkb-hi-signals-2026-10-19_144227 · deployed
2026-10-19 14:42:28 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:c8f92d8c · snapshot:pre-deploy-dkb-kn-signals-2026-10-19_144228 · deployed
2026-10-19 14:43:34 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:78014e9a · snapshot:pre-deploy-maya-hi-signals-2026-10-19_144334 · deployed
2026-10-19 14:43:35 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:dc601ea5 · snapshot:pre-deploy-maya-hi-in-signals-2026-10-19_144335 · deployed
2026-10-19 14:43:36 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:2c7ed2dc · snapshot:pre-deploy-maya-hi-out-2026-10-19_144336 · deployed
2026-10-19 14:43:37 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:62bca725 · snapshot:pre-deploy-maya-hi-in-2026-10-19_144336 · deployed
2026-10-19 14:43:37 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:8f28e21f · snapshot:pre-deploy-kkb-hi-signals-2026-10-19_144337 · deployed
2026-10-19 14:43:38 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:f97b2778 · snapshot:pre-deploy-kkb-kn-signals-2026-10-19_144338 · deployed
2026-10-19 14:43:39 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:ec631883 · snapshot:pre-deploy-kkb-hi-in-signals-2026-10-19_144339 · deployed
2026-10-19 14:43:40 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:cdce77e3 · snapshot:pre-deploy-kkb-kn-in-signals-2026-10-19_144339 · deployed
2026-10-19 14:43:40 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:2d136807 · snapshot:pre-deploy-kkb-hi-out-2026-10-19_144340 · deployed
2026-10-19 14:43:41 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:9d167a51 · snapshot:pre-deploy-kkb-kn-out-2026-10-19_144341 · deployed
2026-10-19 14:43:42 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:1cb41fd5 · snapshot:pre-deploy-kkb-hi-in-2026-10-19_144342 · deployed
2026-10-19 14:43:43 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:affa7e23 · snapshot:pre-deploy-kkb-kn-in-2026-10-19_144342 · deployed
2026-10-19 14:43:43 · prod · dkb-hi-out · 57814ac8-5d79-41f5-bab7-bcfe2d9aac4f · DKB/DKB Hindi.md · sha256:17b1e38c · snapshot:pre-deploy-dkb-hi-out-2026-10-19_144343 · deployed
2026-10-19 14:43:44 · prod · dkb-kn-out · d1a1614f-fa7e-41c1-8963-e7f3af213a13 · DKB/DKB Kannada.md · sha256:95abce61 · snapshot:pre-deploy-dkb-kn-out-2026-10-19_144344 · deployed
2026-10-19 14:57:38 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:f1fc0976 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-19_145735 · deployed
2026-10-19 14:57:42 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:bfadd50b · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-19_145740 · deployed
2026-10-19 15:01:36 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:1a0b47de · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-19_150133 · deployed
2026-10-19 15:01:41 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:f8a11650 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-19_150138 · deployed
2026-10-19 15:08:19 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:edcb5fed · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-19_150818 · deployed
2026-10-19 15:08:19 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:2d7b5d24 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-19_150819 · deployed
2026-10-19 15:16:34 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:015962fe · snapshot:pre-deploy-dkb-hi-signals-2026-10-19_151633 · deployed
2026-10-19 15:16:34 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:64ded050 · snapshot:pre-deploy-dkb-kn-signals-2026-10-19_151634 · deployed
2026-10-19 15:31:10 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:ffc8ce93 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-19_153109 · deployed
2026-10-19 15:31:11 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:f958326c · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-19_153110 · deployed
2026-10-19 15:38:21 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:e8447989 · snapshot:pre-deploy-kkb-hi-out-2026-10-19_153820 · deployed
2026-10-19 15:38:21 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:31bae3ff · snapshot:pre-deploy-kkb-kn-out-2026-10-19_153821 · deployed
2026-10-19 15:38:22 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:7cfe6ec4 · snapshot:pre-deploy-kkb-kn-signals-2026-10-19_153822 · deployed
2026-10-19 15:38:23 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:b94c2135 · snapshot:pre-deploy-kkb-hi-signals-2026-10-19_153823 · deployed
2026-10-19 15:38:24 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:43f6eaed · snapshot:pre-deploy-maya-hi-out-2026-10-19_153824 · deployed
2026-10-19 15:38:25 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:ad93b15d · snapshot:pre-deploy-maya-hi-signals-2026-10-19_153824 · deployed
2026-10-19 15:38:25 · prod · trrain-hi-out · cf39a59a-3b24-4842-ba03-4248ec245aa1 · TRRAIN/TRRAIN Hindi.md · sha256:c8fd61d8 · snapshot:pre-deploy-trrain-hi-out-2026-10-19_153825 · deployed
2026-10-19 15:38:26 · prod · trrain-kn-out · dfeda883-3d2d-4a74-a0b5-1a47fdde2282 · TRRAIN/TRRAIN Kannada.md · sha256:802032a3 · snapshot:pre-deploy-trrain-kn-out-2026-10-19_153826 · deployed
2026-10-19 15:50:20 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:a0213eb0 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-19_155020 · deployed
2026-10-19 15:50:21 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:b2312de2 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-19_155021 · deployed
2026-10-19 15:50:23 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:31f94fac · snapshot:pre-deploy-maya-hi-signals-2026-10-19_155023 · deployed
2026-10-19 15:50:25 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:c53340c0 · snapshot:pre-deploy-maya-hi-in-signals-2026-10-19_155025 · deployed
2026-10-19 15:50:26 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:7f831781 · snapshot:pre-deploy-kkb-hi-signals-2026-10-19_155026 · deployed
2026-10-19 15:50:28 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:d8018c61 · snapshot:pre-deploy-kkb-kn-signals-2026-10-19_155027 · deployed
2026-10-19 15:50:29 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:6bf21511 · snapshot:pre-deploy-kkb-hi-in-signals-2026-10-19_155029 · deployed
2026-10-19 15:50:30 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:91ee2efb · snapshot:pre-deploy-kkb-kn-in-signals-2026-10-19_155030 · deployed
2026-10-19 16:04:05 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:61b0660d · snapshot:pre-deploy-maya-hi-signals-2026-10-19_160404 · deployed
2026-10-19 16:04:06 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:35616025 · snapshot:pre-deploy-maya-hi-in-signals-2026-10-19_160405 · deployed
2026-10-19 16:27:56 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:4657c319 · snapshot:pre-deploy-maya-hi-signals-2026-10-19_162756 · deployed
2026-10-19 16:27:57 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:82114cb1 · snapshot:pre-deploy-maya-hi-in-signals-2026-10-19_162756 · deployed
2026-10-23 12:26:17 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:bbded999 · snapshot:pre-deploy-dkb-hi-signals-2026-10-23_122616 · deployed
2026-10-23 12:26:17 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:694d38da · snapshot:pre-deploy-dkb-kn-signals-2026-10-23_122617 · deployed
2026-10-23 13:06:47 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:d6c9023b · snapshot:pre-deploy-kkb-hi-signals-2026-10-23_130647 · deployed
2026-10-23 13:06:48 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:223469b9 · snapshot:pre-deploy-kkb-kn-signals-2026-10-23_130648 · deployed
2026-10-23 13:06:49 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:43cd092f · snapshot:pre-deploy-kkb-hi-out-2026-10-23_130649 · deployed
2026-10-23 13:06:50 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:66dd0223 · snapshot:pre-deploy-kkb-kn-out-2026-10-23_130649 · deployed
2026-10-23 13:06:50 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:8568e55f · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-23_130650 · deployed
2026-10-23 13:06:51 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:3fa39852 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-23_130651 · deployed
2026-10-23 13:06:52 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:7eac8345 · snapshot:pre-deploy-maya-hi-out-2026-10-23_130652 · deployed
2026-10-23 13:06:53 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:a479bfca · snapshot:pre-deploy-maya-hi-signals-2026-10-23_130652 · deployed
2026-10-23 13:16:50 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:12db70db · snapshot:pre-deploy-kkb-hi-signals-2026-10-23_131649 · deployed
2026-10-23 13:16:51 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:528178e2 · snapshot:pre-deploy-kkb-kn-signals-2026-10-23_131651 · deployed
2026-10-23 13:16:53 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:8a281b00 · snapshot:pre-deploy-kkb-hi-in-signals-2026-10-23_131652 · deployed
2026-10-23 13:16:54 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:bc7403f8 · snapshot:pre-deploy-kkb-kn-in-signals-2026-10-23_131653 · deployed
2026-10-23 13:16:55 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:f99a0143 · snapshot:pre-deploy-kkb-hi-out-2026-10-23_131654 · deployed
2026-10-23 13:16:56 · prod · kkb-hi-in · b6222233-8a8d-49a6-9950-d07e9d159757 · KKB/KKB Placeholder Inbound.md · sha256:dd2a0e11 · snapshot:pre-deploy-kkb-hi-in-2026-10-23_131656 · deployed
2026-10-23 13:16:57 · prod · kkb-kn-in · 4ac90bf1-a740-4b1c-92b0-45bda099e53f · KKB/KKB Placeholder Inbound Kannada.md · sha256:574ad0c5 · snapshot:pre-deploy-kkb-kn-in-2026-10-23_131657 · deployed
2026-10-23 13:16:59 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:b987ca0d · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-23_131658 · deployed
2026-10-23 13:17:00 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:955b85b9 · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-23_131659 · deployed
2026-10-23 13:17:01 · prod · maya-hi-out · 47fdffe6-0cb0-4fcf-8762-135ddadfb194 · Maya/Maya Hindi.md · sha256:18e7065f · snapshot:pre-deploy-maya-hi-out-2026-10-23_131700 · deployed
2026-10-23 13:17:02 · prod · maya-hi-in · df99f501-e636-4f3d-80dc-e06e82240082 · Maya/Maya Inbound.md · sha256:7fb2cbc8 · snapshot:pre-deploy-maya-hi-in-2026-10-23_131701 · deployed
2026-10-23 13:17:03 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:de216eab · snapshot:pre-deploy-maya-hi-signals-2026-10-23_131702 · deployed
2026-10-23 13:17:04 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:a201b158 · snapshot:pre-deploy-maya-hi-in-signals-2026-10-23_131704 · deployed
2026-10-23 13:17:50 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:72462b3f · snapshot:pre-deploy-kkb-hi-signals-2026-10-23_131750 · deployed
2026-10-23 13:17:51 · prod · kkb-hi-out · da612923-1927-45d7-9ad0-b1c7cbb15294 · KKB/KKB Placeholder Hindi.md · sha256:6e2d7e9e · snapshot:pre-deploy-kkb-hi-out-2026-10-23_131751 · deployed
2026-10-23 13:17:52 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:e42fec00 · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-23_131751 · deployed
2026-10-23 13:17:52 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:7b7cef16 · snapshot:pre-deploy-kkb-kn-signals-2026-10-23_131752 · deployed
2026-10-23 13:17:54 · prod · kkb-kn-out · 87ab9108-5d66-4a13-a20a-575eaa9aae36 · KKB/KKB Placeholder Kannada.md · sha256:e20eaa03 · snapshot:pre-deploy-kkb-kn-out-2026-10-23_131753 · deployed
2026-10-23 13:17:54 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:814b8f6b · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-23_131754 · deployed
2026-10-23 13:50:27 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:a681f71f · snapshot:pre-deploy-kkb-hi-signals-2026-10-23_135027 · deployed
2026-10-23 13:50:28 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:7f10a763 · snapshot:pre-deploy-kkb-hi-in-signals-2026-10-23_135028 · deployed
2026-10-23 13:50:29 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:10f5cd77 · snapshot:pre-deploy-maya-hi-signals-2026-10-23_135029 · deployed
2026-10-23 13:50:30 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:92440a2c · snapshot:pre-deploy-maya-hi-in-signals-2026-10-23_135030 · deployed
2026-10-23 15:10:28 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:7e32d38b · snapshot:pre-deploy-kkb-hi-signals-slim-2026-10-23_151028 · deployed
2026-10-23 15:10:29 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:e83dbc3f · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-23_151028 · deployed
2026-10-23 15:10:29 · prod · kkb-hi-signals · 115b38a5-42ef-4082-be69-84a871bb226a · KKB/KKB Placeholder Hindi Signals.md · sha256:c10a252e · snapshot:pre-deploy-kkb-hi-signals-2026-10-23_151029 · deployed
2026-10-23 15:10:30 · prod · kkb-kn-signals · 33037201-78ce-405d-b509-a3b6934e20f1 · KKB/KKB Placeholder Kannada Signals.md · sha256:452b9f83 · snapshot:pre-deploy-kkb-kn-signals-2026-10-23_151030 · deployed
2026-10-23 15:10:31 · prod · kkb-hi-in-signals · 3f521174-574d-43ca-a9be-081849373c18 · KKB/KKB Placeholder Inbound Signals.md · sha256:2a424776 · snapshot:pre-deploy-kkb-hi-in-signals-2026-10-23_151030 · deployed
2026-10-23 15:10:32 · prod · kkb-kn-in-signals · f38da775-c572-4a50-9340-fe1f42c43901 · KKB/KKB Placeholder Inbound Kannada Signals.md · sha256:c2cdf57c · snapshot:pre-deploy-kkb-kn-in-signals-2026-10-23_151031 · deployed
2026-10-23 15:10:32 · prod · maya-hi-signals · 904f333f-1919-4523-a51d-b22ba382dd22 · Maya/Maya Hindi Signals.md · sha256:685e21c6 · snapshot:pre-deploy-maya-hi-signals-2026-10-23_151032 · deployed
2026-10-23 15:10:33 · prod · maya-hi-in-signals · 1c24feda-a584-4012-a865-fa8f950089df · Maya/Maya Inbound Signals.md · sha256:023bd551 · snapshot:pre-deploy-maya-hi-in-signals-2026-10-23_151033 · deployed
2026-10-23 15:10:34 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:fd0985dd · snapshot:pre-deploy-dkb-hi-signals-2026-10-23_151033 · deployed
2026-10-23 15:10:34 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:3df1e237 · snapshot:pre-deploy-dkb-kn-signals-2026-10-23_151034 · deployed
2026-10-23 15:28:49 · prod · kkb-kn-signals-slim · bd4dfd44-a0c5-4d37-9b49-f8c186c901c1 · KKB-Slim/KKB Slim Kannada Signals.md · sha256:87a89e7c · snapshot:pre-deploy-kkb-kn-signals-slim-2026-10-23_152848 · deployed
2026-10-23 15:28:54 · prod · kkb-hi-signals-slim · 140d13ca-c80f-47c4-9454-5edb3fd38c96 · KKB-Slim/KKB Slim Hindi Signals.md · sha256:c74b9bfe · snapshot:- · skip-in-sync
2026-10-23 15:42:41 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:84713a59 · snapshot:pre-deploy-dkb-hi-signals-2026-10-23_154240 · deployed
2026-10-23 15:42:41 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:b75d70ff · snapshot:pre-deploy-dkb-kn-signals-2026-10-23_154241 · deployed
2026-10-26 12:33:31 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:a74aad08 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_123329 · deployed
2026-10-26 12:42:50 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:b0913a31 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_124249 · deployed
2026-10-26 12:43:34 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:f0f9c36e · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_124333 · deployed
2026-10-26 12:56:04 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:706a1beb · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_125603 · deployed
2026-10-26 12:56:06 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:b789f28e · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_125605 · deployed
2026-10-26 15:41:34 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:d8612e98 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_154133 · deployed
2026-10-26 15:41:36 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:417a38d4 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_154135 · deployed
2026-10-26 15:57:56 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:02564bcb · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_155756 · deployed
2026-10-26 15:58:01 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:e4e82e5d · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_155800 · deployed
2026-10-26 16:19:07 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:8020f0f9 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_161906 · deployed
2026-10-26 16:19:07 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:9e28db0c · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_161907 · deployed
2026-10-26 16:41:42 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:d95fdedc · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_164141 · deployed
2026-10-26 16:41:44 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:f71a9207 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_164143 · deployed
2026-10-26 16:51:29 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:149f7c56 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_165129 · deployed
2026-10-26 16:51:30 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:e4d7c77d · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_165130 · deployed
2026-10-26 17:06:36 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:265d1325 · snapshot:pre-deploy-dkb-hi-signals-2026-10-26_170636 · deployed
2026-10-26 17:06:36 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:265d1325 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_170636 · deployed
2026-10-26 17:20:22 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:57b4faf9 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_172022 · deployed
2026-10-26 17:30:11 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:2ea4ee3a · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_173010 · deployed
2026-10-26 17:30:14 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:dd503879 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_173013 · deployed
2026-10-26 17:46:52 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:a09c9557 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_174651 · deployed
2026-10-26 17:46:52 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:2b05d9d5 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_174652 · deployed
2026-10-26 18:07:44 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:7eed6390 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_180744 · deployed
2026-10-26 18:07:45 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:a30a1d35 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_180745 · deployed
2026-10-26 18:23:45 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:1dea22c1 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_182345 · deployed
2026-10-26 18:23:46 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:932ab923 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_182345 · deployed
2026-10-26 18:40:30 · prod · dkb-hi-signals · fabda71d-af75-4ddd-8cf1-fa35c827f753 · DKB/DKB Hindi Signals.md · sha256:f1846858 · snapshot:pre-deploy-dkb-hi-signals-2026-10-26_184030 · deployed
2026-10-26 18:40:31 · prod · dkb-hi-signals-ab · f423c1e0-f801-4e25-93ad-6eb898987b7a · DKB/DKB Hindi Signals.md · sha256:f1846858 · snapshot:pre-deploy-dkb-hi-signals-ab-2026-10-26_184030 · deployed
2026-10-26 18:40:31 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:1d149fd5 · snapshot:pre-deploy-dkb-kn-signals-2026-10-26_184031 · deployed
2026-10-26 18:40:32 · prod · dkb-kn-signals-ab · 4179157d-f8c7-4166-ae38-3431267af298 · DKB/DKB Kannada Signals.md · sha256:1d149fd5 · snapshot:pre-deploy-dkb-kn-signals-ab-2026-10-26_184031 · deployed
2026-10-26 18:40:51 · prod · dkb-kn-signals · 847a85e2-c5c8-4727-9918-f1db9efad05d · DKB/DKB Kannada Signals.md · sha256:1d149fd5 · snapshot:- · skip-in-sync
