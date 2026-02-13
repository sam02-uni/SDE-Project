--
-- PostgreSQL database dump
--

\restrict Sdo00tVOZdGZdh9EZJMqSgEH0HYc4e0vcCoEkMwQX9URjSvV3i8SqOOBkWoUzYs

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: matchday; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.matchday (id, year, number) VALUES (1, '2025/2026', 3);
INSERT INTO public.matchday (id, year, number) VALUES (2, '2025/2026', 22);
INSERT INTO public.matchday (id, year, number) VALUES (3, '2025/2026', 23);
INSERT INTO public.matchday (id, year, number) VALUES (4, '2025/2026', 24);
INSERT INTO public.matchday (id, year, number) VALUES (5, '2025/2026', 25);
INSERT INTO public.matchday (id, year, number) VALUES (6, '2025/2026', 26);
INSERT INTO public.matchday (id, year, number) VALUES (7, '2025/2026', 27);
INSERT INTO public.matchday (id, year, number) VALUES (8, '2025/2026', 28);
INSERT INTO public.matchday (id, year, number) VALUES (9, '2025/2026', 21);
INSERT INTO public.matchday (id, year, number) VALUES (10, '2025/2026', 20);


--
-- Data for Name: matchdaystatus; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (2, 2, 10, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (3, 4, 0, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (1, 3, 10, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (4, 5, 0, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (5, 6, 0, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (6, 7, 0, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (7, 8, 0, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (8, 9, 0, 10);
INSERT INTO public.matchdaystatus (id, matchday_id, played_so_far, total_matches) VALUES (9, 10, 0, 10);


--
-- Name: matchday_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.matchday_id_seq', 10, true);


--
-- Name: matchdaystatus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.matchdaystatus_id_seq', 9, true);


--
-- PostgreSQL database dump complete
--

\unrestrict Sdo00tVOZdGZdh9EZJMqSgEH0HYc4e0vcCoEkMwQX9URjSvV3i8SqOOBkWoUzYs

