SET search_path TO plataforma;

-- Descrição do procedure


CREATE OR REPLACE PROCEDURE criar_ocorrencia(
  IN in_executado_por INT,  -- Todos os procedimentos devem receber este no primeiro parâmetro
  IN in_semestre      INT,
  IN in_grupo         INT
)
LANGUAGE plpgsql
AS $$
DECLARE
   v_grupo_id BIGINT;
BEGIN
  
    -- Verificar permissão
    PERFORM plataforma.verificar_permissao(in_executado_por, 'coordenação');

    -- Inserir na tabela 'ocorreu'
    INSERT INTO ocorreu (semestre, grupo)
    VALUES (in_semestre, in_grupo)
    ON CONFLICT (semestre, grupo) DO NOTHING;

  INSERT INTO log (rotulo, dados)
  VALUES (
    'criar_ocorrencia',                  -- Mesmo nome do procedimento
    jsonb_build_object(
      'executado_por', in_executado_por,
      'semestre',      in_semestre,
      'grupo',         in_grupo
    )
  );
END;
$$;
