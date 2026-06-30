SET search_path TO plataforma;

-- =====================================================
-- B03. Confirmar horas pela apresentação
-- Procedure: confirmar_apresentacao(executado_por, apresentou_id, horas)
-- Por: Vitoria Lima
-- Descrição:
--   Retorna erro se in_horas for negativo e não continua o procedimento.
--   Atualiza a tabela apresentou, definindo confirmado como TRUE.
--   Horas é opcional: se não for NULL, atualiza; caso contrário, mantém.
-- =====================================================

CREATE OR REPLACE PROCEDURE confirmar_apresentacao(
    IN in_executado_por INT,
    IN in_apresentou_id INT,
    IN in_horas NUMERIC DEFAULT NULL
)
LANGUAGE plpgsql
SET search_path = plataforma
AS $$
DECLARE
   v_grupo_id BIGINT;
BEGIN
    -- Buscar o ID do grupo a partir da apresentação
    SELECT o.grupo INTO v_grupo_id
    FROM apresentou a
    JOIN encontro e ON e.id = a.encontro
    JOIN ocorreu o ON o.id = e.ocorrencia
    WHERE a.id = in_apresentou_id;

    -- Verificar permissão de coordenação para este grupo
    PERFORM plataforma.verificar_permissao(in_executado_por, 'coordenação', v_grupo_id);
    
    IF in_horas IS NOT NULL AND in_horas < 0 THEN
        RAISE EXCEPTION 'O valor de horas não pode ser negativo.';
    END IF;

    IF in_horas IS NOT NULL THEN
        UPDATE apresentou
        SET confirmado = TRUE,
            horas = in_horas
        WHERE id = in_apresentou_id;
    ELSE
        UPDATE apresentou
        SET confirmado = TRUE
        WHERE id = in_apresentou_id;
    END IF;
END;
$$;


